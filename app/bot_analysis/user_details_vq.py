
import os
from pprint import pprint
import json

from pandas import DataFrame, read_csv
from scipy.stats import ks_2samp

from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.job import Job
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import date_to_ts
from app.ks_test.interpreter import interpret as interpret_ks, PVAL_MAX

LIMIT = os.getenv("LIMIT") # 1000 # None  # os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25_000")) # 100
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # True

def load_data(csv_filepath):
    if os.path.isfile(csv_filepath) and not DESTRUCTIVE:
        print("LOADING CSV...")
        df = read_csv(csv_filepath)
    else:
        print("DOWNLOADING CSV...")
        df = download_data()
        df.to_csv(csv_filepath, index=False)
    print(fmt_n(len(df)))
    print(df.head())
    return df

def download_data():
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

def ks_test_response(x, y):
    """
    Params x and y : two arrays of sample observations assumed to be drawn from a continuous distribution, sample sizes can be different.
    See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
    """
    xy_result = ks_2samp(x, y)
    response = {
        "stat": xy_result.statistic,
        "pval": xy_result.pvalue,
        "interpret_pval_max": PVAL_MAX,
        "interpret": interpret_ks(xy_result)
    }
    return response

if __name__ == "__main__":

    storage = FileStorage(dirpath="disinformation")
    csv_filepath = os.path.join(storage.local_dirpath, "user_details_vq.csv")
    df = load_data(csv_filepath)

    if input("PERFORM K/S TESTS? (Y/N): ").upper() == "Y":

        print("-----------------------")
        print("TESTING USER CREATION DATES...")

        df["creation_ts"] = df["creation_date"].map(date_to_ts)
        all_timestamps = sorted(df["creation_ts"].tolist())

        print("BOT VS HUMAN...")
        json_filepath = os.path.join(storage.local_dirpath, "ks_test_creation_bots_humans.json")
        x = sorted(df[df["is_bot"] == True]["creation_ts"].tolist())
        y = sorted(df[df["is_bot"] == False]["creation_ts"].tolist())
        print(len(x), len(y), len(x) + len(y) == len(df))
        response = ks_test_response(x, y)
        response["name"] = "User Creation Dates (Bot vs Human)"
        pprint(response)
        with open(json_filepath, "w") as json_file:
            json.dump(response, json_file)

        json_filepath = os.path.join(storage.local_dirpath, "ks_test_creation_disinformation.json")
        x = sorted(df[df["q_status_count"] > 0]["creation_ts"].tolist())
        y = sorted(df[df["q_status_count"] == 0]["creation_ts"].tolist())
        print(f"DISINFORMATION SPREADER ({fmt_n(len(x))}) VS NOT ({fmt_n(len(y))}) ...")
        response = ks_test_response(x, y)
        response["name"] = "User Creation Dates (Disinformation Spreader vs Others)"
        pprint(response)
        with open(json_filepath, "w") as json_file:
            json.dump(response, json_file)
