
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

SERVER_NAME = os.getenv("SERVER_NAME", "mjr-local") # the name of your Heroku app (e.g. "impeachment-tweet-analysis-9")
SERVER_DASHBOARD_URL = f"https://dashboard.heroku.com/apps/{SERVER_NAME}"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def seek_confirmation():
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()
