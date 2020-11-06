from flask import Flask, flash, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from database import get_todos, add_todo, delete_todo
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Todo %r>" % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.id


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # todos = Todo.query.order_by(Todo.created).all()
        todos = get_todos()
        print(todos)
        return render_template("index.html", todos=todos)
    else:
        todo_content = request.form["content"]
        print(todo_content, type(todo_content))
        #new_todo = Todo(content=todo_content)

        try:
            #db.session.add(new_todo)
            #db.session.commit()
            add_todo(todo_content)
            flash("Added!")
            return redirect("/")

        except:
            flash("An error occurred")
            return redirect("/")


@app.route("/delete/<string:todo_id>")
def delete(todo_id):
    #todo_to_delete = Todo.query.get_or_404(todo_id)
    try:
        #db.session.delete(todo_to_delete)
        #db.session.commit()
        print(todo_id)
        delete_todo(todo_id)
        flash("Deleted!")
        return redirect("/")
    except:
        flash("An error occurred")
        return redirect("/")


@app.route("/update/<int:todo_id>", methods=["GET", "POST"])
def update(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == "GET":
        return render_template("update.html", todo=todo)
    else:
        todo.content = request.form["content"]
        try:
            db.session.commit()
            flash("Updated!")
            return redirect("/")
        except:
            flash("An error occurred")
            return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user = request.form["username"]
        pwd = request.form["password"]
        conf = request.form["confirm"]
        pwd_hash = generate_password_hash(pwd, method='pbkdf2:sha256', salt_length=8)

        if not user or not pwd or not conf:
            flash("Please fill in every field")
            return redirect("/register")
        elif pwd != conf:
            flash("Passwords do not match")
            return redirect("/register")

        new_user = User(username=user, password=pwd_hash)

        db.session.add(new_user)
        db.session.commit()

        flash(f"Welcome {user}!")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = request.form["username"]
        pwd = request.form["password"]

        if not user or not pwd:
            flash("Please fill in every field")
            return redirect("/login")

        rows = User.query.filter_by(username=user).all()
        if len(rows) !=1 or not check_password_hash(rows[0].password, pwd):
            flash("Invalid username and/or password")
            return redirect("/login")

        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
