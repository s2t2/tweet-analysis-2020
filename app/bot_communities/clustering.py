import os

from dotenv import load_dotenv
from pandas import DataFrame

import matplotlib.pyplot as plt

from app import seek_confirmation, APP_ENV
from app.bot_communities.bot_similarity_grapher import BotSimilarityGrapher
from app.bot_communities.helper import spectral_clustering

load_dotenv()

K_COMMUNITIES = int(os.getenv("K_COMMUNITIES", default="3"))

if __name__ == "__main__":

    grapher = BotSimilarityGrapher()
    grapher.similarity_graph_report()
    seek_confirmation()

    clusters = spectral_clustering(grapher.similarity_graph, K_COMMUNITIES)
    print("FOUND", len(clusters), "SPECTRAL CLUSTERS:")
    for community_id, community in enumerate(clusters):
        print(f"  CLUSTER {community_id}:", len(community), "USERS")

    seek_confirmation()

    # TODO: move into graph storage
    local_dirpath = os.path.join(grapher.local_dirpath, "k_communities", str(K_COMMUNITIES))
    gcs_dirpath = os.path.join(grapher.gcs_dirpath, "k_communities", str(K_COMMUNITIES))
    local_bot_communities_filepath = os.path.join(local_dirpath, "community_assignments.csv")
    gcs_bot_communities_filepath = os.path.join(gcs_dirpath, "community_assignments.csv")
    if not os.path.exists(local_dirpath):
        os.makedirs(local_dirpath)

    assignments = []
    for community_id, community in enumerate(clusters):
        for user_id in community:
            assignments.append({"user_id": user_id, "community_id": community_id})

    print("----------------")
    print("WRITING COMMUNITY ASSIGNMENTS TO CSV...")
    df = DataFrame(assignments)
    print(df.head())
    df.to_csv(local_bot_communities_filepath)

    print("----------------")
    print("UPLOADING COMMUNITY ASSIGNMENTS TO GCS...")
    grapher.upload_file(local_bot_communities_filepath, gcs_bot_communities_filepath)

    #print("SAVING COMMUNITY ASSIGNMENTS TO BQ...")
    #grapher.insert_community_assignments(assignments)

    #
    # HISTOGRAM
    #

    if APP_ENV == "development":
        plt.hist(df["community_id"])
        plt.grid()
        plt.show()
