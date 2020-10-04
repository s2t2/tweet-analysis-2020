import os

from pandas import read_csv

from app.retweet_graphs_v3.date_range_generator import DateRangeGenerator
from app.retweet_graphs_v3.file_storage import FileStorage
from app.retweet_graphs_v3.retweet_grapher import RetweetGrapher
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

RETWEET_GRAPH_FILENAME = "retweet_graph.gpickle"
BOTS_FILENAME = "bot_probabilities.csv"
BOTS_HISTOGRAM_FILENAME = "bot_probabilities_histogram.png"

if __name__ == "__main__":

    generator = DateRangeGenerator()
    n_days = generator.n_days

    for date_range in generator.date_ranges:
        start_date = date_range.start_date
        end_date = date_range.end_date
        print("START:", start_date)
        print("END:", end_date)

        storage_dirpath = f"retweet_graphs_v3/n_days/{n_days}/{start_date}"
        storage = FileStorage(dirpath=storage_dirpath)

        #
        # RETWEET GRAPH
        #
        if storage.local_file_exists(RETWEET_GRAPH_FILENAME):
            retweet_graph = storage.load_gpickle(RETWEET_GRAPH_FILENAME)
        else:
            retweet_graph = RetweetGrapher(start_date=start_date, end_date=end_date).construct_graph()
            storage.save_gpickle(retweet_graph, filename=RETWEET_GRAPH_FILENAME)

        #
        # BOT CLASSIFICATION
        #
        if storage.local_file_exists(BOTS_FILENAME):
            bots_df = read_csv(BOTS_FILENAME)
        else:
            bot_classifier = BotClassifier(retweet_graph, weight_attr="weight")

            bots_df = bot_classifier.bot_probabilities_df.copy()
            bots_df = bots_df[bots_df["bot_probability"] > 0.5]
            storage.save_df(bots_df, BOTS_FILENAME)

            local_histogram_filepath = storage.local_filepath(BOTS_HISTOGRAM_FILENAME)
            bot_classifier.generate_bot_probabilities_histogram(
                title=f"Bot Probability Scores (excluding 0.5) for Period {start_date} - {end_date}",
                img_filepath=local_histogram_filepath
            )
            storage.upload_file(local_histogram_filepath, storage.gcs_filepath(BOTS_HISTOGRAM_FILENAME))

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

        #seek_confirmation() # might want to review the histogram and choose a different bot min


        #
        # BOT COMMUNITIES
        #
        #breakpoint()

        #bot_subgraph = graph.subgraph(bot_ids) # keeps all bot nodes but only the edges between them, not edges outward
        #bot_subgraph = graph.edge_subgraph(bot_ids) # needs to know full edges

        #bot_graph = DiGraph()
        #for user_id, retweeted_user_id, attrs in graph.edges(data=True):
        #    if user_id in bot_ids:
        #        bot_graph.add_edge(user_id, retweeted_user_id, weight=attrs["weight"])
#
        #    breakpoint()
