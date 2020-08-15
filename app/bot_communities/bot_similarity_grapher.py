
import os

from networkx import write_gpickle

from app import seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.helper import generate_bot_similarity_graph

if __name__ == "__main__":

    grapher = BotRetweetGrapher()

    bot_retweet_graph = grapher.load_graph()

    bot_ids = list(grapher.bq_service.fetch_bot_ids(bot_min=grapher.bot_min))
    print("FETCHED", len(bot_ids), "BOT IDS")

    bot_similarity_graph = generate_bot_similarity_graph(bot_ids, bot_retweet_graph)

    seek_confirmation()

    print("SAVING SIMILARITY GRAPH...")
    local_similarity_graph_filepath = os.path.join(grapher.local_dirpath, "similarity_graph.gpickle")
    write_gpickle(bot_similarity_graph, local_similarity_graph_filepath)

    print("UPLOADING SIMILARITY GRAPH...")
    gcs_similarity_graph_filepath = os.path.join(grapher.gcs_dirpath, "similarity_graph.gpickle")
    grapher.upload_file(local_similarity_graph_filepath, gcs_similarity_graph_filepath)
