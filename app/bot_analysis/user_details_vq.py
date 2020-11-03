
import os

from pandas import DataFrame, read_csv

from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # 1000 # None  # os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25_000")) # 100
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # True

def download_user_details():
    job = Job()
    bq_service = BigQueryService()

    job.start()
    records = []
    for row in bq_service.fetch_user_details_vq(limit=LIMIT):
        #print(row)
        records.append(dict(row))

        job.counter +=1
        if job.counter % BATCH_SIZE == 0:
            job.progress_report()
    job.end()

    return DataFrame(records)

if __name__ == "__main__":

    storage = FileStorage(dirpath="disinformation")

    csv_filepath = os.path.join(storage.local_dirpath, "user_details_vq.csv")
    if os.path.isfile(csv_filepath) and not DESTRUCTIVE:
        print("LOADING CSV...")
        df = read_csv(csv_filepath)
    else:
        print("DOWNLOADING CSV...")
        df = download_user_details()
        df.to_csv(csv_filepath, index=False)
    print(fmt_n(len(df)))
    print(df.head())
