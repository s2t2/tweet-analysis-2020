
import os

from pandas import read_csv

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator

if __name__ == "__main__":
    bq_service = BigQueryService()

    for dr in DateRangeGenerator(start_date="2019-12-20", k_days=1, n_periods=58).date_ranges:
        print(dr.start_date)

        csv_filepath = os.path.join(DATA_DIR, "daily_active_edge_friend_graphs_v5", dr.start_date, "tweets_BERT_Impeachment_800KTweets.csv")
        df = read_csv(csv_filepath, usecols=["status_id", "text", "logit_0", "logit_1", "opinion_tweet"], nrows=100)
        print(df.head())
