
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

if __name__ == "__main__":

    storage = FileStorage(dirpath="disinformation")
    csv_filepath = os.path.join(storage.local_dirpath, "user_details_vq.csv")
    df = load_data(csv_filepath)

    if input("PERFORM K/S TESTS? (Y/N): ").upper() == "Y":

        print("-----------------------")
        print("TESTING USER CREATION DATES...")

        df["creation_ts"] = df["creation_date"].map(date_to_ts)

        print("BOT VS HUMAN...")
        all_timestamps = sorted(df["creation_ts"].tolist())
        bot_timestamps = sorted(df[df["is_bot"] == True]["creation_ts"].tolist())
        human_timestamps = sorted(df[df["is_bot"] == False]["creation_ts"].tolist())
        print(len(bot_timestamps), len(human_timestamps), len(bot_timestamps) + len(human_timestamps) == len(df))

        print("BOTS VS HUMANS")
        bh_result = ks_2samp(bot_timestamps, human_timestamps)
        print(bh_result) #> KstestResult(statistic=0.08727875810101371, pvalue=1.9483380181138512e-159)
        print(interpret_ks(bh_result)) #> 'REJECT (DIFF)'

        ba_result = ks_2samp(all_timestamps, bot_timestamps)
        print(ba_result) #> KstestResult(statistic=0.08669335172277393, pvalue=2.5849735178899478e-157)
        print(interpret_ks(ba_result)) #>'REJECT (DIFF)'

        ha_result = ks_2samp(all_timestamps, human_timestamps)
        print(ha_result) #> KstestResult(statistic=0.0005854063782397834, pvalue=0.5699404349689656)
        print(interpret_ks(ha_result))  #> ACCEPT (SAME)

        response = {
            "name": "User Creation Dates (Bot vs Human)",
            "counts": {
                "all": len(all_timestamps),
                "bot": len(bot_timestamps),
                "human": len(human_timestamps),
            },
            "pval_max": PVAL_MAX,
            "results": {
                "bot_vs_human": {"stat": bh_result.statistic, "pval": bh_result.pvalue, "interpret": interpret_ks(bh_result)},
                "bot_vs_all": {"stat": ba_result.statistic, "pval": ba_result.pvalue, "interpret": interpret_ks(ba_result)},
                "human_vs_all": {"stat": ha_result.statistic, "pval": ha_result.pvalue, "interpret": interpret_ks(ha_result)}
            }
        }
        pprint(response)

        json_filepath = os.path.join(storage.local_dirpath, "ks_test_creation_bots_humans.json")
        with open(json_filepath, "w") as json_file:
            json.dump(response, json_file)


        print(my_data)


        #print("DISINFORMATION SPREADER VS NOT...")




        breakpoint()
