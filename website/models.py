from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',name='user_id'))
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), nullable=True)
    first_name = db.Column(db.String(150), nullable=True)
    notes = db.relationship('Note')
    posts = db.relationship('BlogPost', backref='post_author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)  # New field to check if user is admin
    #is_guest = db.Column(db.Boolean, default=False)  # New field to check if user is guest

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_blogpost_user_id'), nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique session ID for each visitor
    is_guest = db.Column(db.Boolean, default=False)  # New field to check if visitor is guest