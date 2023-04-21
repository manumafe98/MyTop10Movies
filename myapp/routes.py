from flask import Blueprint, render_template, redirect, url_for, request
from forms import EditForm, AddForm
from models import Movies
from extension import db
import requests
import os

API_KEY = os.environ.get("API_KEY")
TBD_SEARCH_API = "https://api.themoviedb.org/3/search/movie"
TBD_GET_API = "https://api.themoviedb.org/3/movie/"
IMAGE_PATH = "https://image.tmdb.org/t/p/w500"
list_of_dicts = []

main = Blueprint("main", __name__)


@main.route("/")
def home():
    all_movies = db.session.query(Movies).order_by(Movies.rating.desc()).all()
    for movie in all_movies:
        ranking = all_movies.index(movie) + 1
        movie_to_edit = Movies.query.filter_by(title=movie.title).first()
        movie_to_edit.ranking = ranking
        db.session.commit()

    return render_template("index.html", movies=all_movies)


@main.route("/edit", methods=["GET", "POST"])
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


@main.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.session.get(Movies, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@main.route("/add", methods=["Get", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.movie_title.data
        r = requests.get(TBD_SEARCH_API, params={"api_key": API_KEY, "query": movie_title})
        output = r.json()
        data = output["results"]
        return render_template("select.html", matched_movies=data)

    return render_template("add.html", form=form)


@main.route("/get_movie_data")
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