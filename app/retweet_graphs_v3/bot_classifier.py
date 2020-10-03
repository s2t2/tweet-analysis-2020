

import os

from app import APP_ENV
from app.file_storage import FileStorage
from app.bq_service import BigQueryService
from app.retweet_graphs_v3.grapher import RetweetGrapher
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    grapher = RetweetGrapher()
    storage = grapher.storage

    graph = grapher.load_graph()
    clf = BotClassifier(graph, weight_attr="weight")

    local_probabilities_filepath = os.path.join(storage.local_dirpath, "probabilities.csv")
    gcs_probabilities_filepath = os.path.join(storage.local_dirpath, "probabilities.csv")
    clf.bot_probabilities_df.to_csv(local_bot_probabilities_filepath)
    storage.upload_file(local_bot_probabilities_filepath, gcs_probabilities_filepath)

    local_histogram_filepath = os.path.join(storage.local_dirpath, "histogram.png")
    gcs_probabilities_filepath = os.path.join(storage.gcs_dirpath, "histogram.png")
    clf.generate_bot_probabilities_histogram(
        img_filepath=local_histogram_filepath, # saves to local file
        title=f"Bot Probability Scores (excluding 0.5) for Period {grapher.start_date} - {grapher.end_date}"
    )
    storage.upload_file(local_histogram_filepath, gcs_probabilities_filepath)

    ## UPLOAD SELECTED ROWS TO BIG QUERY (IF POSSIBLE, OTHERWISE CAN ADD FROM GCS LATER)
    #try:
    #    bots_df = clf.bot_probabilities_df[clf.bot_probabilities_df["bot_probability"] > 0.5]
    #    records = [{**{"start_date": date_range.start_date}, **record}
    #                for record in bots_df.to_dict("records")]
    #    print("UPLOADING", len(records), "BOT SCORES TO BQ...")
    #    bq_service.upload_daily_bot_probabilities(records)
    #
    #except Exception as err:
    #    print("OOPS", err)
