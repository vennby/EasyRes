from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    bios = db.relationship('Bios')
    educations = db.relationship('Educations')
    experiences = db.relationship('Experiences')
    projects = db.relationship('Projects')
    skills = db.relationship('Skills')

class Bios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(160))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Educations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String(100))
    location = db.Column(db.String(50))
    degree = db.Column(db.String(100))
    start_year = db.Column(db.String(10))
    end_year = db.Column(db.String(10))
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
    
class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proj = db.Column(db.String(50))
    tool = db.Column(db.String(50))
    desc = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))