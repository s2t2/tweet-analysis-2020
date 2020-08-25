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

        self.community_assignments = None


    @property
    @lru_cache(maxsize=None)
    def similarity_matrix(self):
        matrix = adjacency_matrix(self.similarity_graph.to_undirected())
        print("SIMILARITY MATRIX", type(matrix))
        return matrix

    def perform(self):
        self.classifier.fit(self.similarity_matrix) # makes the predictions, populates labels
        user_ids = list(self.similarity_graph.nodes())
        community_ids = [label.item() for label in list(self.classifier.labels_)] # converts from np int32 to native python int (so can be stored in BQ without serialization errors)
        iterator = zip(user_ids, community_ids)
        self.community_assignments = [{"user_id": user_id, "community_id": community_id} for user_id, community_id in iterator]

    @property
    @lru_cache(maxsize=None)
    def community_assignments_df(self):
        if not self.community_assignments:
            self.perform()
        df = DataFrame(self.community_assignments)
        df.index.name = "row_id"
        df.index += 1
        return df

    def write_to_file(self):
        print("----------------")
        print("WRITING COMMUNITY ASSIGNMENTS TO CSV...")
        self.community_assignments_df.to_csv(self.local_bot_communities_filepath)

    def upload_to_gcs(self):
        print("----------------")
        print("UPLOADING COMMUNITY ASSIGNMENTS TO GCS...")
        self.grapher.upload_file(self.local_bot_communities_filepath, self.gcs_bot_communities_filepath)

    def save_to_bq(self):
        print("----------------")
        print("SAVING COMMUNITY ASSIGNMENTS TO BQ...")
        self.grapher.bq_service.overwrite_n_bot_communities_table(
            n_communities=self.n_clusters,
            records=self.community_assignments
        )

    def generate_histogram(self):
        print("----------------")
        print("GENERATING COMMUNITIES HISTOGRAM...")
        # todo: optionally customize colors for each series. might be easier to use https://plotly.com/python/histograms/#histogram-with-plotly-express
        plt.hist(self.community_assignments_df["community_id"], color="grey")
        plt.title(f"Bot Communities Histogram (n_communities={self.n_clusters})")
        plt.xlabel("Community Id")
        plt.ylabel("User Count")
        plt.grid()

        img_filepath = os.path.join(self.local_dirpath, "community-assignments.png")
        print(os.path.abspath(img_filepath))
        plt.savefig(img_filepath)
        if APP_ENV == "development":
            plt.show() # this clears the figure, so save before or use reference https://stackoverflow.com/a/9012749/670433

if __name__ == "__main__":

    clustermaker = SpectralClustermaker()

    clustermaker.perform()

    clustermaker.write_to_file()
    clustermaker.upload_to_gcs()
    clustermaker.save_to_bq()

    clustermaker.generate_histogram()
