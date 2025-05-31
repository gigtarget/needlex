from flask import Flask
from app.routes import main
from app.db import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key"
    import os app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    init_db(app)
    app.register_blueprint(main)

    return app
