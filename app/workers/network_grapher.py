
import time
from datetime import datetime
import os
from networkx import DiGraph, write_gpickle

from app.storage_service import BigQueryService, generate_timestamp, bigquery
from app.email_service import send_email

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "follower_network.gpickle")

if __name__ == "__main__":

    service = BigQueryService.cautiously_initialized()
    job = service.fetch_user_friends_in_batches()

    graph = DiGraph()
    counter = 1
    start_at = time.perf_counter()
    for row in job:
        user = row["screen_name"]
        graph.add_node(user)
        for friend in row["friend_names"]:
            graph.add_node(friend)
            graph.add_edge(user, friend)
        counter+=1
        if counter % 1000 == 0: print(generate_timestamp(), counter)

    print("NETWORK GRAPH COMPLETE!")
    end_at = time.perf_counter()
    duration_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {counter} USERS IN {duration_seconds} SECONDS")
    print("NODES:", len(graph.nodes))
    print("EDGES:", len(graph.edges))
    print("SIZE:", graph.size())

    print("WRITING NETWORK GRAPH TO:", os.path.abspath(GPICKLE_FILEPATH))
    write_gpickle(graph, GPICKLE_FILEPATH)
