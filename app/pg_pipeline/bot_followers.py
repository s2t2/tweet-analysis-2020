
import os

from app.pg_pipeline import Pipeline

BOT_MIN = float(os.getenv("BOT_MIN", default="0.8"))

if __name__ == "__main__":

    pipeline = Pipeline()

    pipeline.download_bot_followers(bot_min=BOT_MIN)
