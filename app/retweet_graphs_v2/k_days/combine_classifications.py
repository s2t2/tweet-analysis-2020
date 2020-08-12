
#import os

from pandas import read_csv, DataFrame

#from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator


if __name__ == "__main__":

    combined_df = DataFrame()

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        print("----------")
        print("DATE:", date_range.start_date)
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)

        # TODO: loop through rows (in batches / chunks if necessary),
        # ... find out which ones have a probability greater than the given threshold (need to look at the histogram to choose threshold, probably around 0.8)
        # ... and upload those to bigquery in format {"date":"2020-01-01", "user_id":123, "bot_score": 0.9}

        #df = read_csv(storage.local_bot_probabilities_filepath)
        #print(df.head())

        breakpoint()
