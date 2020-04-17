
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

SERVER_NAME = os.getenv("SERVER_NAME", "mjr-local") # e.g. "impeachment-tweet-analysis-9" on Heroku
SERVER_DASHBOARD_URL = f"https://dashboard.heroku.com/apps/{SERVER_NAME}"
