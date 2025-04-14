from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Experiences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(25))
    comp = db.Column(db.String(25))
    desc = db.Column(db.String(500))
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=True)
    ongoing = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    skills = db.relationship('Skills')
    experiences = db.relationship('Experiences')