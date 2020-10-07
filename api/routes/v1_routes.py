
from flask import Blueprint, current_app, jsonify, request

api_routes = Blueprint("v1_routes", __name__)

@api_routes.route("/api/v1/user_tweets/<screen_name>")
def user_tweets(screen_name=None):
    #print(f"USER TWEETS: '{screen_name}'")
    if "@" in screen_name or ";" in screen_name: # just be super safe about preventing sql injection. there are no screen names with semicolons
        return jsonify({"message": f"Oh, expecting a screen name like 'politico'. Please try again."}), 400

    response = list(current_app.config["BQ_SERVICE"].fetch_user_tweets_api_v1(screen_name))
    try:
        return jsonify([dict(row) for row in response])
    except IndexError as err:
        print(err)
        return jsonify({"message": f"Oh, couldn't find user with screen name '{screen_name}'. Please try again."}), 404
