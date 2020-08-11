
import os

from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)
        storage.report() # loads graph and provides size info

        clf = BotClassifier(storage.graph, weight_attr="weight")

        csv_filename = f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}.csv"
        local_csv_filepath = os.path.join(storage.local_dirpath, csv_filename)
        remote_csv_filepath = os.path.join(storage.gcs_dirpath, csv_filename)
        if not os.path.isfile(local_csv_filepath):
            storage.download_file(remote_csv_filepath, local_csv_filepath)

        img_filename = f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}_histogram.png"
        local_img_filepath = os.path.join(storage.local_dirpath, img_filename)
        remote_img_filepath = os.path.join(storage.gcs_dirpath, img_filename)
        if not os.path.isfile(local_img_filepath):
            storage.download_file(remote_img_filepath, local_img_filepath)

    print("DOWNLOADED ALL!")
