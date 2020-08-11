
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.date_range_generator import DateRangeGenerator
from app.botcode_v2.classifier import NetworkClassifier as BotClassifier

if __name__ == "__main__":

    gen = DateRangeGenerator()

    for date_range in gen.date_ranges:
        storage_dirpath = f"retweet_graphs_v2/k_days/{gen.k_days}/{date_range.start_date}"

        storage = GraphStorage(dirpath=storage_dirpath)
        storage.load_graph()
        storage.report()

        # todo: pass the storage.graph object to the classifier
