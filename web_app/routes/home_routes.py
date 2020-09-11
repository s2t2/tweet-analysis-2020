# web_app/routes/home_routes.py

from flask import Blueprint #, render_template

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
def index():
    print("VISITED THE HOME PAGE")
    #return render_template("dashboard.html")
    return "Welcome Home (TODO)"

@home_routes.route("/about")
def about():
    print("VISITED THE ABOUT PAGE")
    return "About Me (TODO)"

@home_routes.route("/register")
def register():
    print("VISITED THE REGISTRATION PAGE")
    return "Sign Up for our Product! (TODO)"
