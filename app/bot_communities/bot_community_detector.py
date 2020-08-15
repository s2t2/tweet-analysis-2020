import os

from dotenv import load_dotenv
from pandas import DataFrame

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from app import seek_confirmation
from app.bot_communities.bot_similarity_grapher import BotSimilarityGrapher
from app.bot_communities.helper import spectral_clustering

load_dotenv()

K_COMMUNITIES = int(os.getenv("K_COMMUNITIES", default="3"))


if __name__ == "__main__":

    grapher = BotSimilarityGrapher()
    grapher.similarity_graph_report()

    seek_confirmation()

    communities = spectral_clustering(grapher.similarity_graph, K_COMMUNITIES)
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
