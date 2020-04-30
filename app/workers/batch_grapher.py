
from pprint import pprint
import time
from datetime import datetime
import os
from networkx import DiGraph, write_gpickle
from dotenv import load_dotenv

from app.storage_service import BigQueryService, generate_timestamp, bigquery
from app.email_service import send_email

load_dotenv()

# 3.6M users / 180 batches = 20,000 users per batch
# 3.6M users / 360 batches = 10,000 users per batch
# 3.6M users / 720 batches = 5,000 users per batch
N_PARTITIONS = int(os.getenv("N_PARTITIONS", default=360))

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "follower_network.gpickle")

if __name__ == "__main__":

    graph = DiGraph()
    service = BigQueryService.cautiously_initialized()
    start_at = time.perf_counter()

    print("-------------------------")
    print(f"PARTITIONS ({N_PARTITIONS})...")
    partitions = service.partition_user_friends(n=N_PARTITIONS)
    pprint(partitions)

    print("-------------------------")
    counter = 0
    for partition in partitions:
        print(generate_timestamp(),
            f"PROCESSING PARTITION {partition.partition_id} OF {N_PARTITIONS}",
            f"({partition.user_count} USERS, FROM {partition.min_id} TO {partition.max_id})"
        )

        for row in service.fetch_user_friends(min_id=partition.min_id, max_id=partition.max_id):
            counter+=1
            #print("...", row["screen_name"])
            #user = row["screen_name"]
            #graph.add_node(user)
            #for friend in row["friend_names"]:
            #    graph.add_node(friend)
            #    graph.add_edge(user, friend)
    print(counter)

    print("-------------------------")
    print("NETWORK GRAPH COMPLETE!")
    end_at = time.perf_counter()
    duration_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {N_PARTITIONS} USER PARTITIONS IN {duration_seconds} SECONDS")
    print("NODES:", len(graph.nodes))
    print("EDGES:", len(graph.edges))
    print("SIZE:", graph.size())

    print("WRITING NETWORK GRAPH TO:", os.path.abspath(GPICKLE_FILEPATH))
    write_gpickle(graph, GPICKLE_FILEPATH)
