
import os

from pandas import read_csv

from app import DATA_DIR, seek_confirmation
from app.job import Job
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=25000)) # the max number of processed users to store in BQ at once (with a single insert API call)

if __name__ == "__main__":

    bq_service = BigQueryService()
    job = Job()

    print(f"DESTROY PREDICTIONS TABLE? (BERT)")
    seek_confirmation()
    bq_service.nlp_v2_destructively_migrate_predictions_table("bert")
    predictions_table = bq_service.nlp_v2_get_predictions_table("bert")

    job.start()

    for dr in DateRangeGenerator(start_date="2019-12-20", k_days=1, n_periods=58).date_ranges:
        print(dr.start_date)
        csv_filepath = os.path.join(DATA_DIR, "daily_active_edge_friend_graphs_v5", dr.start_date, "tweets_BERT_Impeachment_800KTweets.csv")

        #df = read_csv(csv_filepath, usecols=["status_id", "text", "logit_0", "logit_1", "opinion_tweet"], nrows=100)
        #print(df.head())
        for chunk_df in read_csv(csv_filepath, usecols=["status_id", "logit_0", "logit_1", "opinion_tweet"], chunksize=BATCH_SIZE): # FYI: this will include the last chunk even if it is not a full batch
            chunk_df.rename(columns={"opinion_tweet": "prediction"}, inplace=True)
            #print(chunk_df.head())

            batch = chunk_df.to_dict("records")
            bq_service.insert_records_in_batches(predictions_table, batch)

            job.counter += len(batch)
            job.progress_report()

    job.end()
