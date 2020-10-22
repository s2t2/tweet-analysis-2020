
import os
import json

from pandas import read_csv
import numpy as np

from app import DATA_DIR

#def binned_score(num):

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


if __name__ == "__main__":

    date = "2020-02-01" # todo iterate through dates
    daily_dirpath = os.path.join(DATA_DIR, "retweet_graphs_v2", "k_days", "1", date)
    csv_filepath = os.path.join(daily_dirpath, "bot_probabilities.csv")
    json_histogram_filepath = os.path.join(daily_dirpath, "bot_probabilities_histogram.json")
    #json_filepath = os.path.join(daily_dirpath, "bot_probabilities.json")
    json_bars_filepath = os.path.join(daily_dirpath, "bot_probability_bars.json")

    print("READING CSV", csv_filepath)
    df = read_csv(csv_filepath)
    print(df.head())

    # https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    # hist array The values of the histogram. See density and weights for a description of the possible semantics.
    # bin_edges array of dtype float. Return the bin edges (length(hist)+1).
    hist, bin_edges =  np.histogram(df["bot_probability"], bins=100, range=[0, 1])
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
    print("WRITING HISTOGRAM", json_histogram_filepath)
    with open(json_histogram_filepath, "w") as json_file:
        json.dump(response, json_file)


    #bot_probabilities = df["bot_probability"].tolist()
    #print("WRITING JSON", json_filepath)
    #with open(json_filepath, "w") as json_file:
    #    json.dump(bot_probabilities, json_file)





    #bot_probability_bars = df["bot_probability"].apply(binned_score)

    hist, bin_edges =  np.histogram(df["bot_probability"], bins=20, range=[0, 1]) # in bins of 0.05

    categories = [round(val, 2) for val in bin_edges.tolist()[0:20]] #> [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

    response = [{k: v} for k,v in zip(categories, hist)]
    #> [{0.0: 634}, {0.05: 42}, {0.1: 30}, {0.15: 32}, {0.2: 32}, {0.25: 25}, {0.3: 48}, {0.35: 59}, {0.4: 62}, {0.45: 592}, {0.5: 322649}, {0.55: 2953}, {0.6: 1709}, {0.65: 1251}, {0.7: 1049}, {0.75: 792}, {0.8: 783}, {0.85: 740}, {0.9: 784}, {0.95: 1410}]

    print("WRITING JSON BARS", json_bars_filepath)
    with open(json_bars_filepath, "w") as json_file:
        json.dump(response, json_file, cls=NpEncoder)
