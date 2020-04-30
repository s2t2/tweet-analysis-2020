
import time
from datetime import datetime
import os
from networkx import DiGraph, write_gpickle

from app.storage_service import BigQueryService, generate_timestamp, bigquery
from app.email_service import send_email

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "follower_network.gpickle")

if __name__ == "__main__":

    service = BigQueryService.cautiously_initialized()

    #partitions = [
    #    {"name": "server-01", "min_id": 17                 , "max_id": 49223966           }
    #    {"name": "server-02", "min_id": 49224083           , "max_id": 218645473          }
    #    {"name": "server-03", "min_id": 218645600          , "max_id": 446518003          }
    #    {"name": "server-04", "min_id": 446520525          , "max_id": 1126843322         }
    #    {"name": "server-05", "min_id": 1126843458         , "max_id": 2557922900         }
    #    {"name": "server-06", "min_id": 2557923828         , "max_id": 4277913148         }
    #    {"name": "server-07", "min_id": 4277927001         , "max_id": 833566039577239552 }
    #    {"name": "server-08", "min_id": 833567097506533376 , "max_id": 1012042187482202113}
    #    {"name": "server-09", "min_id": 1012042227844075522, "max_id": 1154556355883089920}
    #    {"name": "server-10", "min_id": 1154556513031266304, "max_id": 1242523027058769920}
    #]

    partitions = service.partition_users(n=180) # 180 batches of 20,000 users
    for partition in partitions:
        #breakpoint()
        print("PROCESSING PARTITION:", partition.partition_id, partition.user_count, partition.min_id, partition.max_id)
        #user_friends = service.fetch_user_friends(min_id=0, max_id=100)
        #for row in user_friends:


    exit()

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
