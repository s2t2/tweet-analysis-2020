
import os

from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)
        storage.report() # loads graph and provides size info

        clf = BotClassifier(storage.graph, weight_attr="weight")

        clf.bot_probabilities_df.to_csv(storage.local_bot_probabilities_filepath)
        storage.upload_bot_probabilities()

        clf.generate_bot_probabilities_histogram(
            img_filepath=storage.local_bot_probabilities_histogram_filepath,
            show_img=(APP_ENV=="development"),
            title=f"Bot Probability Scores for Period '{date_range.start_date}' (excludes 0.5)"
        )
        storage.upload_bot_probabilities_histogram()

        del storage # clear some memory maybe?
        del clf # clear some memory maybe?
        print("\n\n\n\n")

    print("JOB COMPLETE!")
    server_sleep()
