
import os
from dotenv import load_dotenv
from flask import Flask

from api.routes.v0_routes import api_routes as api_v0_routes

from app.bq_service import BigQueryService

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", default="super secret")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["BQ_SERVICE"] = BigQueryService(cautious=False)
    #app.config.from_mapping(SECRET_KEY=SECRET_KEY, BQ_SERVICE=BigQueryService())

    app.register_blueprint(api_v0_routes)
    return app

if __name__ == "__main__":
    my_app = create_app()
    my_app.run(debug=True)
