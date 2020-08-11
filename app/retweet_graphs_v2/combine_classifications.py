
#import os

from pandas import read_csv, DataFrame

#from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator


if __name__ == "__main__":

    combined_df = DataFrame()

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        print("----------")
        print("DATE:", date_range.start_date)
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)

        df = read_csv(storage.local_bot_probabilities_filepath)
        print(df.head())

        breakpoint()
