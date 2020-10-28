
import os

from pandas import DataFrame, read_csv
from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.job import Job

LIMIT = 1000 # None  # os.getenv("LIMIT")
BATCH_SIZE = 90
DESTRUCTIVE = True

#def tweet_stream(limit=LIMIT):
#    bq_service = BigQueryService()
#    return bq_service.fetch_tag_tweets(limit=limit)

def download_tag_tweets():

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

    df = DataFrame(records)
    print(df.head())
    return df

if __name__ == "__main__":


    storage = FileStorage(dirpath="bot_analysis")
    csv_filepath = os.path.join(storage.local_dirpath, "tag_tweets.csv")

    if os.path.isfile(csv_filepath) and not DESTRUCTIVE:
        df = read_csv(csv_filepath)
    else:
        df = download_tag_tweets()


    storage = FileStorage(dirpath="bot_analysis")
    csv_filepath = os.path.join(storage.local_dirpath, "tag_tweets.csv")
    df.to_csv(csv_filepath, index=False)
