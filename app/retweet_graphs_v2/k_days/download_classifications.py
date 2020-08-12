
import os

from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        print("----------")
        print("DATE:", date_range.start_date)
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)

        if not os.path.isfile(storage.local_bot_probabilities_filepath):
            storage.download_bot_probabilities()

        if not os.path.isfile(storage.local_bot_probabilities_histogram_filepath):
            storage.download_bot_probabilities_histogram()

    print("DOWNLOADED ALL!")
