import os
from functools import lru_cache

from dotenv import load_dotenv
from pandas import DataFrame
from networkx import adjacency_matrix, Graph
from sklearn.cluster import SpectralClustering
import matplotlib.pyplot as plt

from app import seek_confirmation, APP_ENV
from app.bot_communities.bot_similarity_grapher import BotSimilarityGrapher


load_dotenv()

N_COMMUNITIES = int(os.getenv("N_COMMUNITIES", default="2"))

class SpectralClustermaker:
    def __init__(self, n_clusters=N_COMMUNITIES):
        self.n_clusters = n_clusters
        self.classifier = SpectralClustering(n_clusters=self.n_clusters, eigen_solver=None, affinity="precomputed", n_init=20)

        self.grapher = BotSimilarityGrapher()
        self.local_dirpath = os.path.join(self.grapher.local_dirpath, "n_communities", str(self.n_clusters))
        self.gcs_dirpath = os.path.join(self.grapher.gcs_dirpath, "n_communities", str(self.n_clusters))
        self.local_bot_communities_filepath = os.path.join(self.local_dirpath, "community_assignments.csv")
        self.gcs_bot_communities_filepath = os.path.join(self.gcs_dirpath, "community_assignments.csv")

        print("-----------------------")
        print("SPECTRAL CLUSTERMAKER")
        print("   N CLUSTERS:", self.n_clusters)
        print("   CLASSIFIER:", type(self.classifier))
        print("   LOCAL DIRPATH:", os.path.abspath(self.local_dirpath))
        print("   GCS DIRPATH:", self.gcs_dirpath)

        seek_confirmation()

        if not os.path.exists(self.local_dirpath):
            os.makedirs(self.local_dirpath)

        self.grapher.similarity_graph_report()  # load bot similarity graph
        self.similarity_graph = self.grapher.similarity_graph


    @property
    @lru_cache(maxsize=None)
    def similarity_matrix(self):
        matrix = adjacency_matrix(self.similarity_graph.to_undirected())
        print("SIMILARITY MATRIX", type(matrix))
        return matrix

    @property
    @lru_cache(maxsize=None)
    def clusters(self):
        return self.classifier.fit(self.similarity_matrix)

    def perform(self):
        communities = [[] for i in range(self.n_clusters)]
        nv = 0 # index for the nodes cluster labels
        for node in self.similarity_graph.nodes():
            breakpoint()
            node_comm = self.classifier.labels_[nv] # community membership of node converted to a python list index
            nv += 1
            X = communities[node_comm] # community list of community c
            X.append(node) # add node to the appropriate community
            communities[node_comm] = X  # add the community list to the big list of all communities
            #print("Node %s joined community %s which has %s nodes"%(node,node_comm,len(Comm[node_comm])))
            communities.sort(reverse=True, key=len)

        self.community_assignments = []
        for community_id, community in enumerate(communities):
            print(f"  CLUSTER {community_id}:", len(community), "USERS")
            for user_id in community:
                self.community_assignments.append({"user_id": user_id, "community_id": community_id})

    @property
    @lru_cache(maxsize=None)
    def community_assignments_df(parameter_list):
        return DataFrame(self.community_assignments)

    def write_to_file(self):
        print("----------------")
        print("WRITING COMMUNITY ASSIGNMENTS TO CSV...")
        self.community_assignments_df.to_csv(self.local_bot_communities_filepath)

    def upload_to_gcs(self):
        print("----------------")
        print("UPLOADING COMMUNITY ASSIGNMENTS TO GCS...")
        self.grapher.upload_file(self.local_bot_communities_filepath, self.gcs_bot_communities_filepath)

    def save_to_bq(self):
        print("SAVING COMMUNITY ASSIGNMENTS TO BQ...")
        self.grapher.bq_service.overwrite_n_bot_communities_table(
            n_communities=self.n_clusters,
            records=self.community_assignments)

    def generate_histogram(self):
        if APP_ENV == "development":
            plt.hist(self.community_assignments_df["community_id"])
            plt.grid()
            plt.show()


if __name__ == "__main__":

    clustermaker = SpectralClustermaker()

    clustermaker.perform()

    clustermaker.write_to_file()
    clustermaker.upload_to_gcs()
    clustermaker.save_to_bq()

    clustermaker.generate_histogram()
