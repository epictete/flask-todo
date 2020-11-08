from flask import flash, render_template, request, redirect, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import app, db, User, Todo
from helpers import login_required, dates, count, define_key


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    dates()
    count()

    if request.method == "GET":
        return redirect("/sort/index/due_asc")
    else:
        todo_content = request.form["content"]
        todo_important = True if ("important" in request.form) else False
        todo_urgent = True if ("urgent" in request.form) else False
        todo_due = datetime.strptime(request.form["due"], "%Y-%m-%d") if (request.form["due"] != "") else None

        if not todo_content:
            flash("Please provide a content.")
            return redirect("/")

        new_todo = Todo(
            content=todo_content,
            important=todo_important,
            urgent=todo_urgent,
            due=todo_due,
            user_id=user_id)

        db.session.add(new_todo)
        db.session.commit()

        flash("Added!")

        return redirect("/")


@app.route("/sort/<string:filter>/<string:sort>")
@login_required
def sort(filter, sort):
    user_id = session["user_id"]
    key = define_key(sort)

    if filter == "index":
        todos = Todo.query.filter(
                Todo.user_id == user_id,
                Todo.archived == None
            ).order_by(key).all()

        return render_template("index.html", todos=todos, sort=sort)
    elif filter == "history":
        todos = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.archived != None
        ).order_by(key).all()

        return render_template("history.html", todos=todos, sort=sort)
    else:
        if filter == "do":
            important = True
            urgent = True
        elif filter == "plan":
            important = True
            urgent = False
        elif filter == "delegate":
            important = False
            urgent = True
        elif filter == "eliminate":
            important = False
            urgent = False

        todos = Todo.query.filter(
                Todo.user_id == user_id,
                Todo.archived == None,
                Todo.important == important,
                Todo.urgent == urgent
            ).order_by(key).all()

        return render_template("filter.html", todos=todos, sort=sort, filter=filter)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)
    todo_to_delete.deleted = True
    todo_to_delete.archived = datetime.utcnow()

    db.session.commit()

    flash("Deleted!")

    return redirect("/")


@app.route("/done/<int:id>")
@login_required
def check(id):
    todo_to_check = Todo.query.get_or_404(id)
    todo_to_check.done = True
    todo_to_check.archived = datetime.utcnow()

    db.session.commit()

    flash("Done!")

    return redirect("/")


@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    todo_to_update = Todo.query.get_or_404(id)

    if request.method == "GET":
        return render_template("update.html", todo=todo_to_update)
    else:
        todo_to_update.content = request.form["content"]
        todo_to_update.important = True if ("important" in request.form) else False
        todo_to_update.urgent = True if ("urgent" in request.form) else False
        todo_to_update.due = datetime.strptime(request.form["due"], "%Y-%m-%d") if (request.form["due"] != "") else None
        todo_to_update.overdue = False if (request.form["due"] == "") else todo_to_update.overdue

        db.session.commit()

        flash("Updated!")

        return redirect("/")


@app.route("/restore/<int:id>")
@login_required
def restore(id):
    todo_to_restore = Todo.query.get_or_404(id)

    if todo_to_restore.done:
        todo_to_restore.done = False
    elif todo_to_restore.deleted:
        todo_to_restore.deleted = False

    todo_to_restore.archived = None

    db.session.commit()

    flash("Restored!")

    return redirect("/")


@app.route("/matrix")
def matrix():
    return render_template("matrix.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        if not username or not password or not confirm:
            flash("Please fill in every field")
            return redirect("/register")
        elif password != confirm:
            flash("Passwords do not match")
            return render_template("register.html", username=username)

        rows = User.query.filter(User.username == username).all()

        if rows:
            flash("Username already taken")
            return redirect("/register")

        new_user = User(username=username, password=hash)

        db.session.add(new_user)
        db.session.commit()

        flash(f"Welcome {username}!")

        return redirect("/matrix")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Please fill in every field")
            return redirect("/login")

        rows = User.query.filter(User.username == username).all()

        if not rows or not check_password_hash(rows[0].password, password):
            flash("Invalid username and/or password")
            return redirect("/login")

        session["user_id"] = rows[0].id
        session["username"] = username

        flash(f"Hello, {username}!")

        return redirect("/")


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    user_id = session["user_id"]
    user_to_update = User.query.get_or_404(user_id)

    if request.method == "GET":
        return render_template("user.html", user=user_to_update)
    else:
        password = request.form["password"]
        confirm = request.form["confirm"]
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        if not password or not confirm:
            flash("Please fill in both fields")
            return redirect("/user")
        elif password != confirm:
            flash("Passwords do not match")
            return redirect("/user")

        user_to_update.password = hash

        db.session.commit()

        flash("Password Updated!")

        return redirect("/user")


@app.route("/logout")
def logout():
    session.clear()

    flash("Goodbye!")

    return redirect("/")


@app.route("/reset", methods=["POST"])
@login_required
def reset():
    user_id = session["user_id"]

    if request.form["confirm"] != "RESET":
        flash("Please type in the correct phrase")
        return redirect("/user")

    todos = Todo.query.filter(Todo.user_id == user_id).all()

    for todo in todos:
        db.session.delete(todo)

    db.session.commit()

    flash("Reset Completed!")

    return redirect("/")


@app.route("/clear", methods=["POST"])
@login_required
def clear():
    user_id = session["user_id"]

    if request.form["confirm"] != "CLEAR":
        flash("Please type in the correct phrase")
        return redirect("/sort/history/archived_desc")

    todos = Todo.query.filter(Todo.user_id == user_id, Todo.archived).all()

    for todo in todos:
        db.session.delete(todo)

    db.session.commit()

    flash("Clear Completed!")

    return redirect("/")


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user_id = session["user_id"]

    if request.form["confirm"] != "DELETE":
        flash("Please type in the correct phrase")
        return redirect("/user")

    todos = Todo.query.filter(Todo.user_id == user_id).all()

    for todo in todos:
        db.session.delete(todo)

    db.session.commit()

    user_to_delete = User.query.filter(User.id == user_id).first()
    db.session.delete(user_to_delete)
    db.session.commit()

    session.clear()
    
    flash("Account Deleted!")

    return redirect("/register")


if __name__ == "__main__":
    app.run(debug=True)
