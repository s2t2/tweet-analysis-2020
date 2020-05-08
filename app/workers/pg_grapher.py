import time
from datetime import datetime as dt
import os
#from dotenv import load_dotenv
from networkx import DiGraph, write_gpickle

from app import DATA_DIR
from app.models import UserFriend, BoundSession
from app.storage_service import generate_timestamp

#load_dotenv()

#BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
#DRY_RUN = (os.getenv("DRY_RUN") == "true")

class NetworkGrapher():

    def __init__(self, graph=DiGraph()):
        self.graph = graph
        self.session = BoundSession()

    def perform(self):
        self.counter = 0
        self.start_at = time.perf_counter()

        print("GENERATING NETWORK GRAPH...")
        for row in self.session.query(UserFriend):
            user = row.screen_name
            friends = row.friend_names
            #self.graph.add_node(user)
            #self.graph.add_nodes_from(friends)
            #self.graph.add_edges_from([(user, friend) for friend in friends])

            self.counter+=1
            if self.counter % 1000 == 0:
                print(generate_timestamp(), self.counter)

        print("NETWORK GRAPH COMPLETE!")
        self.end_at = time.perf_counter()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

        #print("NODES:", len(self.graph.nodes))
        #print("EDGES:", len(self.graph.edges))
        #print("SIZE:", self.graph.size())

    def write_to_file(self, graph_filepath):
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)

if __name__ == "__main__":

    grapher = NetworkGrapher()
    grapher.perform()
    grapher.report()

    timestamp = dt.now().strftime("%Y_%m_%d_%H_%M")
    graph_filepath = os.path.join(DATA_DIR, f"follower_network_{timestamp}.gpickle")
    #grapher.write_to_file(graph_filepath)
