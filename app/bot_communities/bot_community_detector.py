import os

from dotenv import load_dotenv
from networkx import read_gpickle
from pandas import DataFrame

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from app import seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.helper import spectral_clustering

load_dotenv()

K_COMMUNITIES = int(os.getenv("K_COMMUNITIES", default="3"))

def load_similarity_graph():
    print("LOADING SIMILARITY GRAPH...")
    # TODO: refactor these paths into the BotRetweetGrapher storage service
    grapher = BotRetweetGrapher()
    local_similarity_graph_filepath = os.path.join(grapher.local_dirpath, "similarity_graph.gpickle")
    gcs_similarity_graph_filepath = os.path.join(grapher.gcs_dirpath, "similarity_graph.gpickle")
    if not os.path.isfile(local_similarity_graph_filepath):
        grapher.download_file(gcs_similarity_graph_filepath, local_similarity_graph_filepath)

    return read_gpickle(local_similarity_graph_filepath)


if __name__ == "__main__":

    bot_similarity_graph = load_similarity_graph()
    print("SIMILARITY GRAPH:", type(bot_similarity_graph), bot_similarity_graph.number_of_nodes())

    breakpoint()
    seek_confirmation()

    communities = spectral_clustering(bot_similarity_graph, K_COMMUNITIES)
    print("FOUND", len(communities), "SPECTRAL COMMUNITIES")
    print(type(communities))

    for community_id, community in enumerate(communities):
        print(f"RETWEET COMMUNITY {community_id}:", len(community), "NODES")

    breakpoint()

    # SAVE TO CSV

    df = DataFrame()
    communities_map = {}

    for community_id, community in enumerate(communities):
        for v in community:
            communities_map[v] = community_id

    community_list = []
    for v in df.screen_name:
        if v in communities_map:
            community_list.append(communities_map[v])
        else:
            community_list.append(-1)

    df["community"] = community_list
    df.to_csv(local_bot_communities_csv_filepath)

    plt.hist(df_profiles.Community)
    plt.grid()
    plt.show()
