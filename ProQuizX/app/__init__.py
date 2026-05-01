from flask import Flask
from .database import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-this-secret-key-in-production"
    app.config["DATABASE"] = "quiz_app.db"

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        init_db()

    return app
