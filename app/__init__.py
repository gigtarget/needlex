# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to login if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Config for Railway (or .env fallback)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Replace or load from env
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Change to PostgreSQL on Railway
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register Blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
