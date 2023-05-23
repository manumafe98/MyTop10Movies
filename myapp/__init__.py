from flask import Flask
from flask_bootstrap import Bootstrap
from myapp.extension import db
from myapp.routes import main
import os

# https://www.youtube.com/watch?v=WhwU1-DLeVw&t=3s&ab_channel=PrettyPrinted
# $env:API_KEY = "38d089808acd67f9a32d59629a4578a8"
# $env:SECRET_KEY = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///movies.db")
    db.init_app(app)
    app.register_blueprint(main)

    Bootstrap(app)

    return app
