

import os
from pandas import read_csv, DataFrame

from app.file_storage import FileStorage
from app.bq_service import BigQueryService
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # for development purposes
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="10_000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # whether or not to re-download if a local file already exists

if __name__ == "__main__":

    bq_service = BigQueryService()
    job = Job()

    storage = FileStorage(dirpath=f"user_details_v6")

    tweets_csv_filepath = os.path.join(storage.local_dirpath, "tweets.csv")
    if os.path.exists(tweets_csv_filepath) and not DESTRUCTIVE:
        print("LOADING TWEETS...")
        tweets_df = read_csv(tweets_csv_filepath)
    else:
        job.start()
        print("DOWNLOADING TWEETS...")
        records = []
        for row in bq_service.fetch_tweet_details_v6(limit=LIMIT):
            records.append(dict(row))
            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        tweets_df = DataFrame(records)
        tweets_df.to_csv(tweets_csv_filepath, index=False)

    print("TWEETS:", fmt_n(len(tweets_df)))
