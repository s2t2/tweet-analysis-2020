# web_app/routes/home_routes.py

from flask import Blueprint, render_template

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    print("VISITED THE HOME PAGE")
    return render_template("home.html")

@home_routes.route("/about")
def about():
    print("VISITED THE ABOUT PAGE")
    return render_template("about.html")

@home_routes.route("/prototype/politico")
def events():
    print("PROTOTYPE: POLITICO")
    return render_template("prototype_politico.html")
