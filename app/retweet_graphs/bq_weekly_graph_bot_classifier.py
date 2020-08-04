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

    local_artifacts_dir = os.path.join(storage_service.local_dirpath, "botcode_v2")
    if not os.path.isdir(local_artifacts_dir):
        os.mkdir(local_artifacts_dir)
    remote_artifacts_dir = os.path.join(storage_service.gcs_dirpath, "botcode_v2")

    if DRY_RUN:
        local_csv_filepath = os.path.join(local_artifacts_dir, "mock_probabilities.csv")
        local_img_filepath = os.path.join(local_artifacts_dir, "mock_probabilities_histogram.png")
        remote_csv_filepath = os.path.join(remote_artifacts_dir, "mock_probabilities.csv")
        remote_img_filepath = os.path.join(remote_artifacts_dir, "mock_probabilities_histogram.png")
    else:
        local_csv_filepath = os.path.join(local_artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}.csv")
        local_img_filepath = os.path.join(local_artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}_histogram.png")
        remote_csv_filepath = os.path.join(remote_artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}.csv")
        remote_img_filepath = os.path.join(remote_artifacts_dir, f"bot_probabilities_{classifier.lambda_00}_{classifier.lambda_11}_histogram.png")

    print("----------------")
    print("SAVING CSV FILE...")
    print(local_csv_filepath)
    df.to_csv(local_csv_filepath)
    storage_service.gcs_service.upload(local_csv_filepath, remote_csv_filepath)

    print("----------------")
    print("SAVING HISTOGRAM...")
    print(local_img_filepath)
    classifier.generate_bot_probabilities_histogram(img_filepath=local_img_filepath, show_img=(APP_ENV=="development"))
    storage_service.gcs_service.upload(local_img_filepath, remote_img_filepath)
