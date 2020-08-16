
import os

from networkx import write_gpickle, read_gpickle, jaccard_coefficient, Graph

from app import seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
#from app.bot_communities.helper import generate_bot_similarity_graph
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n

class BotSimilarityGrapher(BotRetweetGrapher):

    def __init__(self):
        super().__init__()
        self.similarity_graph = None

    @property
    def retweet_graph(self):
        return self.graph

    def retweet_graph_report(self):
        self.report()

    def perform(self):
        """
        Params:
            bot_ids (list) a unique list of bot ids, which should all be included as nodes in the bot retweet graph.
                The retweet graph will also contain retweeted users. So that's why we need a separate list.
                The bot ids will be used as nodes in the similarity graph.

            bot_retweet_graph (networkx.DiGraph) a retweet graph generated from the bot list

        Returns a similarity graph (networkx.Graph), where the similarity is based on the Jaccard index.
            For each pair of bots we calculate the Jaccard index based on the sets of people they retweet.
            If two bots retweet exactly the same users, their Jaccard index is one.
            If they don't retweet anyone in common, their Jaccard index is zero.
        """

        grapher.retweet_graph_report()

        bot_ids = [row.user_id for row in self.bq_service.fetch_bot_ids(bot_min=self.bot_min)]
        print("FETCHED", fmt_n(len(bot_ids)), "BOT IDS")

        node_pairs = []
        for i, bot_id in enumerate(bot_ids):
            for other_bot_id in bot_ids[i+1:]:
                if self.retweet_graph.has_node(other_bot_id) and self.retweet_graph.has_node(bot_id):
                    node_pairs.append((bot_id, other_bot_id))
        # this step is maybe unnecessary because we
        # could maybe just take the combinations between all nodes in the bot graph
        # (because we can assume they were assembled using the same bot ids as the ones here)
        # but the point is to be methodologically sound and it doesn't take that long
        print("NODE PAIRS:", fmt_n(len(node_pairs)))

        results = jaccard_coefficient(self.retweet_graph.to_undirected(), node_pairs)
        #> returns an iterator of 3-tuples in the form (u, v, p)
        #> where (u, v) is a pair of nodes and p is their Jaccard coefficient.
        print("JACCARD COEFFICIENT RESULTS:", fmt_n(len(results)))

        print("CONSTRUCTING SIMILARITY GRAPH...")
        self.similarity_graph = Graph()
        edge_count = 0
        #positive_results = [r for r in results if r[2] > 0] # this takes a while, maybe let's just stick with the original iterator approach
        for bot_id, other_bot_id, similarity_score in results:
            if similarity_score > 0:
                self.similarity_graph.add_edge(bot_id, other_bot_id, weight=similarity_score)
                edge_count += 1

            self.counter += 1
            if self.counter % self.batch_size == 0:
                print(logstamp(), "|", fmt_n(self.counter), "|", fmt_n(edge_count), "EDGES")

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

    def write_similarity_graph(self):
        print("SAVING SIMILARITY GRAPH...")
        write_gpickle(self.similarity_graph, self.local_similarity_graph_filepath)

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
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.similarity_graph_report()
    grapher.save_similarity_graph()
