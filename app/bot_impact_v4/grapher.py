
import os

from pandas import DataFrame, read_csv

from app.job import Job
from app.bq_service import BigQueryService
from app.file_storage import FileStorage

DATE = os.getenv("DATE", default="2020-01-23")
TWEET_MIN = os.getenv("TWEET_MIN")
LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true")

if __name__ == "__main__":

    print("------------------------")
    print("GRAPHER...")
    print("  DATE:", DATE)
    print("  TWEET_MIN:", TWEET_MIN)
    print("  LIMIT:", LIMIT)
    print("  BATCH_SIZE:", BATCH_SIZE)
    print("  DESTRUCTIVE:", DESTRUCTIVE)

    print("------------------------")
    storage = FileStorage(dirpath=f"daily_active_friend_graphs_v4/{DATE}/tweet_min/{TWEET_MIN}")
    tweets_csv_filepath = os.path.join(storage.local_dirpath, "tweets.csv")

    bq_service = BigQueryService()
    job = Job()

    #
    # DAILY TWEETS
    # tweet_id, text, screen_name, bot, created_at
    if os.path.exists(tweets_csv_filepath) and not DESTRUCTIVE:
        statuses_df = read_csv(tweets_csv_filepath)
        print(len(statuses_df))
    else:
        job.start()
        statuses = []
        for row in bq_service.fetch_daily_active_tweeter_statuses(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT):
            statuses.append(dict(row))

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        statuses_df = DataFrame(statuses)
        print(len(statuses_df))
        del statuses
        statuses_df.to_csv(tweets_csv_filepath)
