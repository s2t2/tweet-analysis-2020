
import os

from networkx import write_gpickle

from app import seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.helper import generate_bot_similarity_graph

class BotSimilarityGrapher(BotRetweetGrapher):

    @property
    def retweet_graph(self):
        return self.graph

    @property
    def retweet_graph_report(self):
        self.report()

    #
    # BOT SIMILARITY GRAPH STORAGE
    #   TODO: refactor into a new storage service to inherit from the base storage service,
    #   and mix that in instead (requires some parent class de-coupling)
    #

    @property
    def local_similarity_graph_filepath(self):
        return os.path.join(self.local_dirpath, "similarity_graph.gpickle")

    @property
    def gcs_similarity_graph_filepath(self):
        return os.path.join(self.gcs_dirpath, "similarity_graph.gpickle")

    def write_similarity_graph(self, bot_similarity_graph):
        print("SAVING SIMILARITY GRAPH...")
        write_gpickle(self.bot_similarity_graph, self.local_similarity_graph_filepath)

    def upload_similarity_graph(self):
        print("UPLOADING SIMILARITY GRAPH...")
        self.upload_file(self.local_similarity_graph_filepath, self.gcs_similarity_graph_filepath)

    def load_similarity_graph(self):
        print("LOADING SIMILARITY GRAPH...")
        if not os.path.isfile(self.local_similarity_graph_filepath):
            self.download_file(self.gcs_similarity_graph_filepath, self.local_similarity_graph_filepath)

        return read_gpickle(self.local_similarity_graph_filepath)

    def save_similarity_graph(self):
        self.write_similarity_graph()
        self.upload_similarity_graph()

    def similarity_graph_report(self):
        if not self.similarity_graph:
            self.similarity_graph = self.load_similarity_graph()

        print("-------------------")
        print("SIMILARITY GRAPH", type(self.similarity_graph))
        print("  NODES:", fmt_n(self.similarity_graph.number_of_nodes()))
        print("  EDGES:", fmt_n(self.similarity_graph.number_of_edges()))
        print("-------------------")

if __name__ == "__main__":

    grapher = BotSimilarityGrapher()
    grapher.retweet_graph_report()

    bot_ids = list(grapher.bq_service.fetch_bot_ids(bot_min=grapher.bot_min))
    print("FETCHED", len(bot_ids), "BOT IDS")

    grapher.similarity_graph = generate_bot_similarity_graph(bot_ids, grapher.retweet_graph)

    grapher.similarity_graph_report()
    grapher.save_similarity_graph()
