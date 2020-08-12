
import os

from app import APP_ENV, server_sleep
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier
from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"
        storage = GraphStorage(dirpath=storage_dirpath)
        storage.report() # loads graph and provides size info

        clf = BotClassifier(storage.graph, weight_attr="weight")

        clf.bot_probabilities_df.to_csv(storage.local_bot_probabilities_filepath)
        storage.upload_bot_probabilities()

        rows_to_insert = []
        for row in clf.bot_probabilities_df[clf.bot_probabilities_df["bot_probability"] > 0.5]
            rows_to_insert.append({
                "start_date": date_range.start_date,
                "user_id": row["user_id"],
                "bot_probability": row["bot_probability"],
            })
        bq_service.upload_daily_bot_probabilities(rows_to_insert)

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
