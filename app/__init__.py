from flask import Flask
from app.routes import main
from app.db import init_db
import os

def create_app():
    app = Flask(__name__)

    # 🔐 Use SECRET_KEY from Railway or fallback if not set
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback123")

    # 🛢️ Use PostgreSQL from Railway environment variable
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    init_db(app)
    app.register_blueprint(main)

    return app
