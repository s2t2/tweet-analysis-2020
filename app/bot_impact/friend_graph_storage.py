
import os
import pickle
import json
from pprint import pprint

from memory_profiler import profile
from networkx import write_gpickle #,read_gpickle

from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.file_storage import FileStorage

class FriendGraphStorage(FileStorage):
    def  __init__(self, dirpath):
        super().__init__(dirpath=dirpath)

        self.local_metadata_filepath = os.path.join(self.local_dirpath, "metadata.json")
        self.gcs_metadata_filepath = os.path.join(self.gcs_dirpath, "metadata.json")

        self.local_nodes_filepath = os.path.join(self.local_dirpath, "nodes.csv")
        self.gcs_nodes_filepath = os.path.join(self.gcs_dirpath, "nodes.csv")

        self.local_histogram_filepath = os.path.join(self.local_dirpath, "histogram.png")
        self.gcs_histogram_filepath = os.path.join(self.gcs_dirpath, "histogram.png")

        self.local_graph_filepath = os.path.join(self.local_dirpath, "graph.gpickle")
        self.gcs_graph_filepath = os.path.join(self.gcs_dirpath, "graph.gpickle")

        self.local_subgraph_filepath = os.path.join(self.local_dirpath, "subgraph.gpickle")
        self.gcs_subgraph_filepath = os.path.join(self.gcs_dirpath, "subgraph.gpickle")

    def save_metadata(self):
        print(logstamp(), "SAVING METADATA...")
        with open(self.local_metadata_filepath, "w") as f:
            json.dump(self.metadata, f)
        self.upload_file(self.local_metadata_filepath, self.gcs_metadata_filepath)

    def save_nodes(self):
        print(logstamp(), "SAVING NODES...")
        self.nodes_df.to_csv(self.local_nodes_filepath)
        self.upload_file(self.local_nodes_filepath, self.gcs_nodes_filepath)

    def save_graph(self):
        print(logstamp(), "SAVING GRAPH...")
        write_gpickle(self.graph, self.local_graph_filepath)
        self.upload_file(self.local_graph_filepath, self.gcs_graph_filepath)

    def save_subgraph(self):
        print(logstamp(), "SAVING SUBGRAPH...")
        write_gpickle(self.subgraph, self.local_graph_filepath)
        self.upload_file(self.local_subgraph_filepath, self.gcs_subgraph_filepath)

    def report(self, graph):
        print("-------------------")
        print(type(graph))
        print("  NODES:", fmt_n(graph.number_of_nodes()))
        print("  EDGES:", fmt_n(graph.number_of_edges()))
        print("-------------------")

    def graph_report(self):
        self.report(self.graph)

    def subgraph_report(self):
        self.report(self.subgraph)


    # AFTER YOU HAVE ALREADY SAVED THE ARTIFACTS...

    #@profile
    #def load_graph(self):
    #    """Assumes the graph already exists and is saved locally or remotely"""
    #    if not os.path.isfile(self.local_graph_filepath):
    #        self.download_graph()
#
    #    return self.read_graph_from_file()

    #@profile
    #def load_subgraph(self):
    #    """Assumes the subgraph already exists and is saved locally or remotely"""
    #    if not os.path.isfile(self.local_subgraph_filepath):
    #        self.download_subgraph()
    #
    #    return self.read_subgraph_from_file()
