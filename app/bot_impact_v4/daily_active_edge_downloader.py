

import os
from pandas import read_csv, DataFrame


from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator
from app.file_storage import FileStorage
from app.bq_service import BigQueryService
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # for development purposes
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # whether or not to re-download if a local file already exists

if __name__ == "__main__":

    gen = DateRangeGenerator(k_days=1)
    bq_service = BigQueryService()
    job = Job()

    for dr in gen.date_ranges:
        print(dr.start_date)
        storage = FileStorage(dirpath=f"daily_active_edge_friend_graphs_v5/{dr.start_date}")
        tweets_csv_filepath = os.path.join(storage.local_dirpath, "tweets.csv")
        nodes_csv_filepath = os.path.join(storage.local_dirpath, "nodes.csv")

        if os.path.exists(tweets_csv_filepath) and not DESTRUCTIVE:
            print("LOADING TWEETS...")
            tweets_df = read_csv(tweets_csv_filepath)
        else:
            job.start()
            print("DOWNLOADING TWEETS...")
            records = []
            for row in bq_service.fetch_daily_statuses_with_opinion_scores(date=dr.start_date, limit=LIMIT):
                records.append(dict(row))
                job.counter += 1
                if job.counter % BATCH_SIZE == 0:
                    job.progress_report()
            job.end()
            tweets_df = DataFrame(records)
            tweets_df.to_csv(tweets_csv_filepath)
            del records
        print("TWEETS:", fmt_n(len(tweets_df)))

        if os.path.exists(nodes_csv_filepath) and not DESTRUCTIVE:
            print("LOADING NODES...")
            nodes_df = read_csv(nodes_csv_filepath)
        else:
            job.start()
            print("DOWNLOADING NODES...")
            records = []
            for row in bq_service.fetch_daily_nodes_with_active_edges(date=dr.start_date, limit=LIMIT):
                records.append(dict(row))
                job.counter += 1
                if job.counter % BATCH_SIZE == 0:
                    job.progress_report()
            job.end()
            nodes_df = DataFrame(records)
            nodes_df.to_csv(nodes_csv_filepath)
            del records
        print("NODES:", fmt_n(len(nodes_df)))
