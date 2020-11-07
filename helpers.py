from functools import wraps
from flask import session, redirect
from datetime import date, timedelta

from db import db, Todo


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def urgent():
    user_id = session["user_id"]
    todos = Todo.query.filter(Todo.user_id == user_id, Todo.due != None).all()

    for todo in todos:
        if (todo.due - date.today()) <= timedelta(days=1):
            todo.urgent = True

    db.session.commit()


def overdue():
    user_id = session["user_id"]
    todos = Todo.query.filter(Todo.user_id == user_id, Todo.due != None).all()

    for todo in todos:
        if (todo.due - date.today()) < timedelta(days=0):
            todo.overdue = True
        else:
            todo.overdue = False

    db.session.commit()


def count():
    user_id = session["user_id"]

    session["do"] = Todo.query.filter(
            Todo.important == True, Todo.urgent == True, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).count()
    session["plan"] = Todo.query.filter(
            Todo.important == True, Todo.urgent == False, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).count()
    session["delegate"] = Todo.query.filter(
            Todo.important == False, Todo.urgent == True, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).count()
    session["eliminate"] = Todo.query.filter(
            Todo.important == False, Todo.urgent == False, Todo.user_id == user_id, Todo.done == False, Todo.deleted == False
        ).count()
