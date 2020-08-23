import os
from dotenv import load_dotenv

load_dotenv()

START_AT = os.getenv("START_AT", default="2019-12-10")
END_AT = os.getenv("END_AT", default="2020-02-10")

from app.pg_pipeline import Pipeline

if __name__ == "__main__":

    pipeline = Pipeline()

    print("START_AT:", START_AT)
    print("END AT:", END_AT)

    pipeline.download_tweets(start_at=START_AT, end_at=END_AT) # takes about X minutes for X tweets in batches of 2500
