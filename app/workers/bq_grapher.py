
import time
from datetime import datetime as dt
import os
from networkx import DiGraph, write_gpickle

from app import DATA_DIR
from app.bq_service import BigQueryService, generate_timestamp, bigquery
from app.email_service import send_email

class NetworkGrapher():
    def __init__(self, graph=None, bq=None):
        self.graph = (graph or DiGraph())
        self.bq = (bq or BigQueryService.cautiously_initialized())

    def perform(self):
        self.counter = 1
        self.start_at = time.perf_counter()
        for row in self.bq.fetch_user_friends_in_batches():
            user = row["screen_name"]
            friends = row["friend_names"]

            self.graph.add_node(user)
            self.graph.add_nodes_from(friends)
            self.graph.add_edges_from([(user, friend) for friend in friends])

            self.counter+=1
            if self.counter % 1000 == 0: print(generate_timestamp(), self.counter)

        print("NETWORK GRAPH COMPLETE!")
        self.end_at = time.perf_counter()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

        print("NODES:", len(self.graph.nodes))
        print("EDGES:", len(self.graph.edges))
        print("SIZE:", self.graph.size())

    def write_to_file(self, graph_filepath):
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)

if __name__ == "__main__":

    grapher = NetworkGrapher()

    grapher.perform()

    grapher.report()

    timestamp = dt.now().strftime("%Y_%m_%d_%H_%M")
    graph_filepath = os.path.join(DATA_DIR, f"follower_network_{timestamp}.gpickle")
    grapher.write_to_file(graph_filepath)
