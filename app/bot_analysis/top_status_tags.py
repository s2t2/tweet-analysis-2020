
import os

from pandas import DataFrame, read_csv
import re

from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # 1000 # None  # os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25_000")) # 100
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # True

TWITTER_PATTERN = r'[^a-zA-Z ^0-9 # @]' # alphanumeric, plus hashtag and handle symbols (twitter-specific)

def download_tweets():
    job = Job()
    bq_service = BigQueryService()

    job.start()
    records = []
    for row in bq_service.fetch_tag_tweets(limit=LIMIT): #tweet_stream():
        #print(row)
        records.append(dict(row))

        job.counter +=1
        if job.counter % BATCH_SIZE == 0:
            job.progress_report()
    job.end()

    return DataFrame(records)

def parse_hashtags(status_text):
    txt = re.sub(TWITTER_PATTERN, "", status_text.upper())
    tags = [token.upper() for token in status_text.split() if token.startswith("#") and not token.endswith("#")]
    return tags

if __name__ == "__main__":

    storage = FileStorage(dirpath="bot_analysis")

    tweets_csv_filepath = os.path.join(storage.local_dirpath, "tag_tweets.csv")
    if os.path.isfile(tweets_csv_filepath) and not DESTRUCTIVE:
        print("LOADING TWEETS...")
        tweets_df = read_csv(tweets_csv_filepath)
    else:
        print("DOWNLOADING TWEETS...")
        tweets_df = download_tweets()
        tweets_df.to_csv(tweets_csv_filepath, index=False)
    print(fmt_n(len(tweets_df)))
    print(tweets_df.head())

    print("ANALYZING TWEETS...")
    tags_csv_filepath = os.path.join(storage.local_dirpath, "top_status_tags.csv")
    #tags_df = analyze_tweets(tweets_df)
    #tags_df.to_csv(tags_csv_filepath, index=False)

    tweets_df["status_tags"] = tweets_df["status_text"].apply(parse_hashtags)

    breakpoint()
    tweets_df.to_csv(tags_csv_filepath)
