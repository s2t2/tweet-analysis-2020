
from app.pg_pipeline import Pipeline

if __name__ == "__main__":

    pipeline = Pipeline()

    pipeline.download_daily_bot_probabilities()
