from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

ENV = "prod"

if ENV == "dev":
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
else:
    app.debug = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kzxthmhxusewtx:584aec8bab830632973fc663d29e7847d8bc2b1d3879d62cd909d55b6301f5d1@ec2-34-206-252-187.compute-1.amazonaws.com:5432/dc52ammeo2tbrd"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

    def __repr__(self):
        return "<User %r>" % self.id


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(120), nullable=False)
    important = db.Column(db.Boolean, nullable=False)
    urgent = db.Column(db.Boolean, nullable=False)
    overdue = db.Column(db.Boolean, default=False)
    done = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    due = db.Column(db.Date)
    archived = db.Column(db.DateTime)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "<Todo %r>" % self.id
