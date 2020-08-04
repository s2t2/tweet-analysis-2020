import os

from conftest import compile_mock_rt_graph
from app import APP_ENV, seek_confirmation
from app.retweet_graphs.bq_weekly_grapher import BigQueryWeeklyRetweetGrapher
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier, DRY_RUN

if __name__ == "__main__":

    storage_service = BigQueryWeeklyRetweetGrapher.init_storage_service()

    # LOAD RT GRAPH

    if DRY_RUN:
        rt_graph = compile_mock_rt_graph()
    else:
        rt_graph = storage_service.load_graph()
    storage_service.report(rt_graph)
    seek_confirmation()

    # PERFORM BOT CLASSIFICATION

    classifier = BotClassifier(rt_graph)
    df = classifier.bot_probabilities_df

    # SAVE ARTIFACTS

    artifacts_dir = os.path.join(storage_service.local_dirpath, "botcode_v2")
    if not os.path.isdir(artifacts_dir):
        os.mkdir(artifacts_dir)

    if DRY_RUN:
        csv_filepath = os.path.join(artifacts_dir, "mock_probabilities.csv")
        img_filepath = os.path.join(artifacts_dir, "mock_probabilities_histogram.png")
    else:
        csv_filepath = os.path.join(artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}.csv")
        img_filepath = os.path.join(artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}_histogram.png")

    print("----------------")
    print("SAVING CSV FILE...")
    print(csv_filepath)
    df.to_csv(csv_filepath)

    print("----------------")
    print("SAVING HISTOGRAM...")
    print(img_filepath)
    classifier.generate_bot_probabilities_histogram(img_filepath=img_filepath, show_img=(APP_ENV=="development"))
