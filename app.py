from flask import flash, render_template, request, redirect, session
from sqlalchemy import or_
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from db import app, db, User, Todo
from helpers import login_required, urgent, overdue, count


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]

    urgent()
    overdue()
    count()

    if request.method == "GET":
        return redirect("/sort/due_asc")
    else:
        todo_content = request.form["content"]
        todo_important = True if ("important" in request.form) else False
        todo_urgent = True if ("urgent" in request.form) else False
        todo_due = datetime.strptime(request.form["due"], "%Y-%m-%d") if (request.form["due"] != "") else None

        if not todo_content:
            flash("Please provide a content.")
            return redirect("/")

        new_todo = Todo(content=todo_content, important=todo_important, urgent=todo_urgent, due=todo_due, user_id=user_id)

        try:
            db.session.add(new_todo)
            db.session.commit()
            flash("Added!")

        except:
            flash("An error occurred")

        return redirect("/")


@app.route("/sort/<string:type>")
@login_required
def sort(type):
    user_id = session["user_id"]

    if type == "todo_asc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.content).all()
    elif type == "todo_desc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.content.desc()).all()
    elif type == "created_asc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.created).all()
    elif type == "created_desc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.created.desc()).all()
    elif type == "due_asc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.due).all()
    elif type == "due_desc":
        todos = Todo.query.filter(
            Todo.user_id == user_id, Todo.done == False, Todo.deleted == False).order_by(
            Todo.due.desc()).all()

    return render_template("index.html", todos=todos, sort=type)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)
    todo_to_delete.deleted = True

    try:
        db.session.commit()
        flash("Deleted!")

    except:
        flash("An error occurred")

    return redirect("/")


@app.route("/done/<int:id>")
@login_required
def check(id):
    todo_to_check = Todo.query.get_or_404(id)
    todo_to_check.done = True

    try:
        db.session.commit()
        flash("Done!")

    except:
        flash("An error occurred")

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

        try:
            db.session.commit()
            flash("Updated!")

        except:
            flash("An error occurred")

        return redirect("/")


@app.route("/filter/<string:type>")
@login_required
def filter(type):
    user_id = session["user_id"]

    if type == "do":
        todos = Todo.query.filter(
            Todo.important == True, Todo.urgent == True, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).order_by(Todo.due).all()
        return render_template("filter.html", todos=todos, filter=type)
    elif type == "plan":
        todos = Todo.query.filter(
            Todo.important == True, Todo.urgent == False, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).order_by(Todo.due).all()
        return render_template("filter.html", todos=todos, filter=type)
    elif type == "delegate":
        todos = Todo.query.filter(
            Todo.important == False, Todo.urgent == True, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).order_by(Todo.due).all()
        return render_template("filter.html", todos=todos, filter=type)
    elif type == "eliminate":
        todos = Todo.query.filter(
            Todo.important == False, Todo.urgent == False, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).order_by(Todo.due).all()
        return render_template("filter.html", todos=todos, filter=type)


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    todos = Todo.query.filter(
        Todo.user_id == user_id, or_(Todo.done == True, Todo.deleted == True)
    ).order_by(Todo.created.desc()).all()
    return render_template("history.html", todos=todos)


@app.route("/matrix")
def matrix():
    return render_template("matrix.html")


@app.route("/restore/<int:id>")
@login_required
def restore(id):
    todo_to_restore = Todo.query.get_or_404(id)

    if todo_to_restore.done:
        todo_to_restore.done = False
    elif todo_to_restore.deleted:
        todo_to_restore.deleted = False

    try:
        db.session.commit()
        flash("Restored!")

    except:
        flash("An error occurred")

    return redirect("/")


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

        rows = User.query.filter_by(username=username).all()

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

        rows = User.query.filter_by(username=username).all()

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
            return redirect(f"/user/{id}")
        elif password != confirm:
            flash("Passwords do not match")
            return redirect(f"/user/{id}")

        user_to_update.password = hash

        try:
            db.session.commit()
            flash("Password Updated!")

        except:
            flash("An error occurred")

        return redirect("/user")


@app.route("/logout")
def logout():
    session.clear()
    flash("Goodbye!")
    return redirect("/")


@app.route("/reset", methods=["POST"])
@login_required
def reset():
    if request.form["confirm"] != "RESET":
        flash("Please type in the correct requested phrase")
        return redirect("/user")

    user_id = session["user_id"]

    todos = Todo.query.filter(Todo.user_id == user_id).all()

    for todo in todos:
        db.session.delete(todo)
        db.session.commit()

    flash("Reset Completed!")
    return redirect("/")


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    if request.form["confirm"] != "DELETE":
        flash("Please type in the correct requested phrase")
        return redirect("/user")

    user_id = session["user_id"]

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
