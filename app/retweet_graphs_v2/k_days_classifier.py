
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
        clf = BotClassifier(storage.load_graph(), weight_attr="weight")

        csv_filename = f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}.csv"
        local_csv_filepath = os.path.join(storage.local_dirpath, csv_filename)
        remote_csv_filepath = os.path.join(storage.gcs_dirpath, csv_filename)
        clf.bot_probabilities_df.to_csv(local_csv_filepath)
        storage.upload_file(local_csv_filepath, remote_csv_filepath)

        img_filename = f"bot_probabilities_{clf.lambda_00}_{clf.lambda_11}_histogram.png"
        local_img_filepath = os.path.join(storage.local_dirpath, img_filename)
        remote_img_filepath = os.path.join(storage.gcs_dirpath, img_filename)
        clf.generate_bot_probabilities_histogram(img_filepath=local_img_filepath, show_img=(APP_ENV=="development"))
        storage.upload_file(local_img_filepath, remote_img_filepath)

        del storage # clear some memory maybe?
        del clf # clear some memory maybe?
        server_sleep(5*60) # maybe mini nap for 5 minutes to cool memory?
        print("\n\n\n\n")

    print("JOB COMPLETE!")
    server_sleep()
