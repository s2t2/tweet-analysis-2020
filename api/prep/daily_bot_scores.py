
import os
import json

from pandas import read_csv
from numpy import histogram

from app import DATA_DIR

if __name__ == "__main__":

    date = "2020-02-01" # todo iterate through dates
    daily_dirpath = os.path.join(DATA_DIR, "retweet_graphs_v2", "k_days", "1", date)
    csv_filepath = os.path.join(daily_dirpath, "bot_probabilities.csv")
    json_filepath = os.path.join(daily_dirpath, "bot_probabilities_histogram.json")

    print("READING CSV", csv_filepath)
    df = read_csv(csv_filepath)
    print(df.head())

    # https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    # hist array The values of the histogram. See density and weights for a description of the possible semantics.
    # bin_edges array of dtype float. Return the bin edges (length(hist)+1).

    hist, bin_edges =  histogram(df["bot_probability"], bins=100, range=[0, 1])
    print("HIST:", len(list(hist))) #> 100
    print("BIN EDGES:", len(list(bin_edges))) #> 101

    # weird, but https://formidable.com/open-source/victory/docs/victory-histogram/
    # turns out VictoryHistogram likes this format, so lets just convert it to json...

    response = {
        "date": date,
        "hist": hist.tolist(),
        "bin_edges": [round(v.item(), 2)  for v in bin_edges] # round to 2 decimal places because dealing with some vals like 0.35000000000000003 ewww
    }
    print(response)

    print("WRITING JSON", json_filepath)
    with open(json_filepath, "w") as json_file:
        json.dump(response, json_file)
