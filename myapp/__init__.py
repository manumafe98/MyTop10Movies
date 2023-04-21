from flask import Flask
from flask_bootstrap import Bootstrap
from myapp.extension import db
from routes import main
import os


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///blog.db")
    db.init_app(app)
    app.register_blueprint(main)
    Bootstrap(app)

    return app
