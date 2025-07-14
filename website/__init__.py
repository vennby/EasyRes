import os
from flask import Flask
from flask_login import LoginManager
from .models import db, User, Skills  # assuming db is defined in models.py
from os import path

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "development-key")

    # Choose DB URI: PostgreSQL on Render, SQLite locally
    if "DATABASE_URL" in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.sign_in'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    # Only check for file existence in local (SQLite)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        if not path.exists(DB_NAME):
            db.create_all()
            print('Created SQLite Database!')
    else:
        # Always try to create tables in production (PostgreSQL)
        db.create_all()
        print('Initialized PostgreSQL Database!')
