# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from app.models import db, User
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Secret key for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Use PostgreSQL on Railway or fallback to local SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register Blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
