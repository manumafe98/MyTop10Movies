from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "38d089808acd67f9a32d59629a4578a8"
TBD_SEARCH_API = "https://api.themoviedb.org/3/search/movie"
TBD_GET_API = "https://api.themoviedb.org/3/movie/"
IMAGE_PATH = "https://image.tmdb.org/t/p/w500"
list_of_dicts = []

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy(app)


class EditForm(FlaskForm):
    rating = StringField(label="Your Rating", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class AddForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), unique=True, nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = db.session.query(Movies).order_by(Movies.rating.desc()).all()
    for movie in all_movies:
        ranking = all_movies.index(movie) + 1
        movie_to_edit = Movies.query.filter_by(title=movie.title).first()
        movie_to_edit.ranking = ranking
        db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        movie_id = request.args.get("id")
        movie_to_update = db.session.get(Movies, movie_id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.session.get(Movies, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["Get", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.movie_title.data
        r = requests.get(TBD_SEARCH_API, params={"api_key": API_KEY, "query": movie_title})
        output = r.json()
        data = output["results"]
        return render_template("select.html", matched_movies=data)

    return render_template("add.html", form=form)


@app.route("/get_movie_data")
def get_movie_data():
    movie_id = int(request.args.get("id"))
    movie_api_url = f"{TBD_GET_API}/{movie_id}"
    r = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
    output = r.json()
    new_record = Movies(title=output["original_title"],
                        description=output["overview"],
                        year=output["release_date"].split("-")[0],
                        img_url=f"{IMAGE_PATH}{output['poster_path']}",
                        rating=1.0,
                        ranking="None",
                        review="")
    db.session.add(new_record)
    db.session.commit()
    get_movie = Movies.query.filter_by(title=output["original_title"]).first()
    get_id = get_movie.id
    return redirect(url_for("edit", id=get_id))


if __name__ == "__main__":
    app.run(debug=True)
