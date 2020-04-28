
import os
from networkx import DiGraph, write_gpickle

from app.storage_service import BigQueryService

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "follower_network.gpickle")

if __name__ == "__main__":

    graph = DiGraph()

    service = BigQueryService.cautiously_initialized()

    user_friends = service.fetch_user_friends(limit=100) # TODO: fetch in batches
    for row in user_friends:
        user = row.screen_name
        graph.add_node(user)

        for friend in row.friend_names:
            graph.add_node(friend)
            graph.add_edge(user, friend)

    print("NETWORK GRAPH COMPLETE!")
    print("NODES:", len(graph.nodes))
    print("EDGES:", len(graph.edges))
    print("SIZE:", graph.size())

    print("WRITING NETWORK GRAPH TO:", os.path.abspath(GPICKLE_FILEPATH))
    write_gpickle(graph, GPICKLE_FILEPATH)
