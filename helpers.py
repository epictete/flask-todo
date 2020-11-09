from functools import wraps
from flask import session, redirect
from datetime import date, timedelta
from db import db, Todo


def dates():
    user_id = session["user_id"]
    todos = Todo.query.filter(Todo.user_id == user_id, Todo.due != None).all()

    for todo in todos:
        if (todo.due - date.today()) <= timedelta(days=1):
            todo.urgent = True

        if (todo.due - date.today()) < timedelta(days=0):
            todo.important = True
            todo.overdue = True
        else:
            todo.overdue = False

    db.session.commit()


def count():
    user_id = session["user_id"]

    session["do"] = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.important == True,
            Todo.urgent == True,
            Todo.done == False,
            Todo.deleted == False
        ).count()
    session["plan"] = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.important == True,
            Todo.urgent == False,
            Todo.done == False,
            Todo.deleted == False
        ).count()
    session["delegate"] = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.important == False,
            Todo.urgent == True,
            Todo.done == False,
            Todo.deleted == False
        ).count()
    session["eliminate"] = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.important == False,
            Todo.urgent == False,
            Todo.done == False,
            Todo.deleted == False
        ).count()
    session["history"] = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.archived != None
        ).count()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        dates()
        count()
        return f(*args, **kwargs)
    return decorated_function


def define_key(sort):
    if sort == "content_asc":
        key = Todo.content
    elif sort == "content_desc":
        key = Todo.content.desc()
    elif sort == "created_asc":
        key = Todo.created
    elif sort == "created_desc":
        key = Todo.created.desc()
    elif sort == "due_asc":
        key = Todo.due
    elif sort == "due_desc":
        key = Todo.due.desc()
    elif sort == "archived_asc":
        key = Todo.archived
    elif sort == "archived_desc":
        key = Todo.archived.desc()

    return key
