import os

from app.retweet_graphs_v3.date_range_generator import DateRangeGenerator
from app.retweet_graphs_v3.file_storage import FileStorage
from app.retweet_graphs_v3.retweet_grapher import RetweetGrapher

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
        local_retweet_graph_filepath = os.path.join(storage.local_dirpath, "retweet_graph.gpickle")

        if not storage.file_exists("retweet_graph.gpickle"):
            retweet_graph = RetweetGrapher(start_date=start_date, end_date=end_date).construct_graph()
            storage.save_gpickle_as(retweet_graph, filename="retweet_graph.gpickle")

        #if not os.path.exists(storage.local_bot_probabilities_filepath):
