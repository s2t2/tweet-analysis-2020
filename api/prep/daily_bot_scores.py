
import os
import json

from pandas import read_csv
from numpy import histogram

from app import DATA_DIR

if __name__ == "__main__":

    date = "2020-02-01" # todo iterate through dates

    df = read_csv(os.path.join(DATA_DIR, "retweet_graphs_v2", "k_days", "1", date, "bot_probabilities.csv"))

    breakpoint()

    #print(df["bot_probability"].value_counts())

    #df["bp_binned"] = df["bot_probability"]
    histo = histogram(df["bot_probability"], bins=100)
