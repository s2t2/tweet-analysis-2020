
import os
#import time
import gc

from dotenv import load_dotenv

from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier
from app.bq_service import BigQueryService

load_dotenv()

SKIP_EXISTING = (os.getenv("SKIP_EXISTING", default="true") == "true")

if __name__ == "__main__":

    bq_service = BigQueryService()

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)

        if SKIP_EXISTING and storage.gcs_service.file_exists(storage.gcs_bot_probabilities_histogram_filepath):
            # would check for CSV file but it seems checking for larger file sometimes leads to
            # urllib3.exceptions.ProtocolError: ('Connection aborted.', OSError(0, 'Error')),
            # so check the smaller histogram file instead
            print("FOUND EXISTING BOT PROBABILITIES. SKIPPING...")
            continue # skip to next date range

        print("PROCEEDING WITH CLASSIFICAITON...")
        storage.report() # loads graph and provides size info
        clf = BotClassifier(storage.graph, weight_attr="weight")

        # UPLOAD COMPLETE CSV TO GOOGLE CLOUD STORAGE
        clf.bot_probabilities_df.to_csv(storage.local_bot_probabilities_filepath)
        storage.upload_bot_probabilities()

        # UPLOAD COMPLETE HISTOGRAM TO GOOGLE CLOUD STORAGE
        clf.generate_bot_probabilities_histogram(
            img_filepath=storage.local_bot_probabilities_histogram_filepath,
            show_img=(APP_ENV=="development"),
            title=f"Bot Probability Scores for Period '{date_range.start_date}' (excludes 0.5)"
        )
        storage.upload_bot_probabilities_histogram()

        # UPLOAD SELECTED ROWS TO BIG QUERY (IF POSSIBLE, OTHERWISE CAN ADD FROM GCS LATER)
        try:
            bots_df = clf.bot_probabilities_df[clf.bot_probabilities_df["bot_probability"] > 0.5]
            records = [{**{"start_date": date_range.start_date}, **record} for record in bots_df.to_dict("records")]
            print("UPLOADING", len(records), "BOT SCORES TO BQ...")
            bq_service.upload_daily_bot_probabilities(records)

            del bots_df
            del records
        except Exception as err:
            print("OOPS", err)

        del storage
        del clf
        gc.collect()
        print("\n\n\n\n")

    print("JOB COMPLETE!")
    server_sleep()
