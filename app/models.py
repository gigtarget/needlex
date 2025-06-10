# app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user')  # 'admin' or 'user'

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref='machines')  # ✅ Required for template
    heads = db.relationship('Head', backref='machine', cascade="all, delete-orphan")

class Head(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'))

class NeedleChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.id'))
    needle_number = db.Column(db.Integer, nullable=False)
    needle_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
