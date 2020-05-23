import os

from networkx import DiGraph, write_gpickle
from pandas import DataFrame
#from memory_profiler import profile

from app import DATA_DIR
from app.workers.psycopg_base_grapher import BaseGrapher

class TestGrapher():

    #@profile
    def perform(self):
        self.edges = set() # prevents duplicates

        batch =[
            {"screen_name":"A", "friend_names":["B", "C", "D"]},
            {"screen_name":"B", "friend_names":["C", "D"]},
            {"screen_name":"C", "friend_names":["D"]},
            {"screen_name":"D", "friend_names":["C"]},
            {"screen_name":"E", "friend_names":["F"]},
        ]
        for row in batch:
            user = row["screen_name"]
            friends = row["friend_names"]
            self.edges.update([(user, friend) for friend in friends])

        self.graph = DiGraph(list(self.edges))

        graph_filepath = os.path.join(DATA_DIR, "follower_network_example.gpickle")
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)


if __name__ == "__main__":

    grapher = TestGrapher()
    grapher.perform()
