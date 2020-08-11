
import os

from app import APP_ENV
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"

        storage = GraphStorage(dirpath=storage_dirpath)

        clf = BotClassifier(storage.load_graph(), weight_attr="weight")

        csv_filepath = os.path.join(storage_dirpath, f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}.csv")
        clf.bot_probabilities_df.to_csv(csv_filepath)

        img_filepath = os.path.join(storage_dirpath, f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}_histogram.png")
        clf.generate_bot_probabilities_histogram(img_filepath=img_filepath, show_img=(APP_ENV=="development"))
