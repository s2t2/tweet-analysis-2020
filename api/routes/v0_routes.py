
from flask import Blueprint, current_app, jsonify

api_routes = Blueprint("v0_routes", __name__)

@api_routes.route("/api/v0/user_details/<screen_name>")
def user_details(screen_name=None):
    print("USER TWEETS (WITH PREDICTIONS) / ", screen_name)
    if "@" in screen_name or ";" in screen_name:
        # just be super safe about preventing sql injection. there are no screen names with semicolons
        return jsonify({"message": f"Oh, expecting a screen name like 'politico'. Please try again."}), 400

    bq_service = current_app.config["BQ_SERVICE"]
    response = list(bq_service.fetch_user_details_api_v0(screen_name))
    try:
        parsed_response = dict(response[0])
        return jsonify(parsed_response)
    except IndexError as err:
        print(err)
        return jsonify({"message": f"Oh, couldn't find user with screen name '{screen_name}'. Please try again."}), 404
    except:
        return jsonify({"message": f"Oh, something unexpected happened. Please try again."}), 400
