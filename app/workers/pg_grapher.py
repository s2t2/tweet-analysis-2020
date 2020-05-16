import time
from datetime import datetime as dt
import os
from dotenv import load_dotenv
from networkx import DiGraph, write_gpickle

from app import DATA_DIR, APP_ENV
from app.models import UserFriend, BoundSession, USER_FRIENDS_TABLE_NAME
from app.storage_service import generate_timestamp

load_dotenv()

DRY_RUN = (os.getenv("DRY_RUN", default="true") == "true")

class NetworkGrapher():

    def __init__(self, dry_run=DRY_RUN, graph=None, table_name=None):
        self.session = BoundSession()
        self.table_name = (table_name or USER_FRIENDS_TABLE_NAME)
        self.dry_run = (dry_run == True)
        self.graph = (graph or DiGraph())

    @classmethod
    def cautiously_initialized(cls):
        service = cls()
        print("-------------------------")
        print("NETWORK GRAPHER CONFIG...")
        print("  PG TABLE NAME:", service.table_name.upper())
        print("  DRY RUN:", str(service.dry_run).upper())
        print("-------------------------")
        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        return service

    def perform(self):
        self.counter = 0
        self.start_at = time.perf_counter()

        if not self.dry_run:
            print("GENERATING NETWORK GRAPH...")

        for row in self.session.query(UserFriend):
            user = row.screen_name
            friends = row.friend_names
            if not self.dry_run:
                self.graph.add_node(user)
                self.graph.add_nodes_from(friends)
                self.graph.add_edges_from([(user, friend) for friend in friends])

            self.counter+=1
            if self.counter % 1000 == 0:
                print(generate_timestamp(), self.counter)

        print("JOB COMPLETE!")
        self.end_at = time.perf_counter()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")
        if self.graph:
            print("NODES:", len(self.graph.nodes))
            print("EDGES:", len(self.graph.edges))
            print("SIZE:", self.graph.size())

    def write_to_file(self, graph_filepath):
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)

if __name__ == "__main__":

    grapher = NetworkGrapher.cautiously_initialized()




    breakpoint()



    grapher.perform()
    grapher.report()

    if any(grapher.graph.nodes):
        timestamp = dt.now().strftime("%Y_%m_%d_%H_%M")
        graph_filepath = os.path.join(DATA_DIR, f"follower_network_{timestamp}.gpickle")
        grapher.write_to_file(graph_filepath)
