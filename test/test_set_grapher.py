import os
import pickle

from networkx import DiGraph, write_gpickle
from pandas import DataFrame
from memory_profiler import profile

from app import DATA_DIR

class TestGrapher():

    @profile
    def perform(self):
        self.edges = set() # prevents duplicates

        batch =[
            {"screen_name":"A", "friend_names":["B", "C", "D"]},
            {"screen_name":"B", "friend_names":["C", "D"]},
            {"screen_name":"C", "friend_names":["D"]},
            {"screen_name":"D", "friend_names":["C"]},
            {"screen_name":"E", "friend_names":["F"]},
        ]

        # CONSTRUCT EDGES

        for row in batch:
            user = row["screen_name"]
            friends = row["friend_names"]
            self.edges.update([(user, friend) for friend in friends])

        # WRITE EDGES

        edges_filepath = os.path.join(DATA_DIR, "my_edges.gpickle")
        print("WRITING EDGES TO:", os.path.abspath(edges_filepath))
        with open(edges_filepath, "wb") as pickle_file:
            pickle.dump(self.edges, pickle_file)

        # CONSTRUCT GRAPH

        self.graph = DiGraph(list(self.edges))

        # WRITE GRAPH

        graph_filepath = os.path.join(DATA_DIR, "my_graph.gpickle")
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)


if __name__ == "__main__":

    grapher = TestGrapher()
    grapher.perform()
