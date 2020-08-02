
import os
import json
import pickle

from pandas import DataFrame
from networkx import DiGraph, write_gpickle

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.gcs_service import GoogleCloudStorageService

class GraphStorage:

    def __init__(self, local_dirpath=None, gcs_dirpath=None, gcs_service=None):
        """
        Abstract class to support the saving of artifacts during the networkx graph compilation process.

        Params:
            local_dirpath (str) like "path/to/my/local/dir"
            gcs_dirpath (str) like "path/to/gcs/bucket/dir"
        """
        self.local_dirpath = local_dirpath or os.path.join(DATA_DIR, "graphs", "storage_example")
        self.gcs_dirpath = gcs_dirpath or os.path.join("storage", "data", "graphs", "storage_example")
        self.gcs_service = gcs_service or GoogleCloudStorageService()

        print("----------------------------")
        print("GRAPH STORAGE")
        print("   LOCAL DIR:", self.local_dirpath)
        print("   GCS DIR:", self.local_dirpath)

        seek_confirmation()

        if not os.path.exists(self.local_dirpath):
            os.mkdir(self.local_dirpath)

        #self.metadata = {}
        #self.running_results = []
        #self.edges = []
        #self.graph = None # DiGraph()

    #
    # LOCAL STORAGE
    #

    @property
    def local_metadata_filepath(self):
        return os.path.join(self.local_dirpath, "metadata.json")

    @property
    def local_results_filepath(self):
        return os.path.join(self.local_dirpath, "results.csv")

    @property
    def local_edges_filepath(self):
        return os.path.join(self.local_dirpath, "edges.gpickle")

    @property
    def local_graph_filepath(self):
        return os.path.join(self.local_dirpath, "graph.gpickle")

    def write_metadata_to_file(self, metadata_filepath=None):
        print(logstamp(), "WRITING METADATA...")
        metadata_filepath = metadata_filepath or self.local_metadata_filepath
        with open(metadata_filepath, "w") as metadata_file:
            json.dump(self.metadata, metadata_file)

    def write_results_to_file(self, results_filepath=None):
        print(logstamp(), "WRITING RESULTS...")
        results_filepath = results_filepath or self.local_results_filepath
        df = DataFrame(self.running_results)
        df.to_csv(results_filepath)

    def write_edges_to_file(self, edges_filepath=None):
        print(logstamp(), "WRITING EDGES...:")
        edges_filepath = edges_filepath or self.local_edges_filepath
        with open(edges_filepath, "wb") as pickle_file:
            pickle.dump(self.edges, pickle_file)

    def write_graph_to_file(self, graph_filepath=None):
        print(logstamp(), "WRITING GRAPH...")
        graph_filepath = graph_filepath or self.local_graph_filepath
        write_gpickle(self.graph, graph_filepath)

    #
    # REMOTE STORAGE
    #

    @property
    def gcs_metadata_filepath(self):
        return os.path.join(self.gcs_dirpath, "metadata.json")

    @property
    def gcs_results_filepath(self):
        return os.path.join(self.gcs_dirpath, "results.csv")

    @property
    def gcs_edges_filepath(self):
        return os.path.join(self.gcs_dirpath, "edges.gpickle")

    @property
    def gcs_graph_filepath(self):
        return os.path.join(self.gcs_dirpath, "graph.gpickle")

    def upload_metadata(self):
        print(logstamp(), "UPLOADING JOB METADATA...", self.gcs_metadata_filepath)
        blob = self.gcs_service.upload(self.local_metadata_filepath, self.gcs_metadata_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_results(self):
        print(logstamp(), "UPLOADING JOB RESULTS...", self.gcs_results_filepath)
        blob = self.gcs_service.upload(self.local_results_filepath, self.gcs_results_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_edges(self):
        print(logstamp(), "UPLOADING NETWORK EDGES...", self.gcs_edges_filepath)
        blob = self.gcs_service.upload(self.local_edges_filepath, self.gcs_edges_filepath)
        print(logstamp(), blob)

    def upload_graph(self):
        print(logstamp(), "UPLOADING GRAPH...", self.gcs_graph_filepath)
        blob = self.gcs_service.upload(self.local_graph_filepath, self.gcs_graph_filepath)
        print(logstamp(), blob)

if __name__ == "__main__":

    example_storage = GraphStorage()

    print(example_storage.local_dirpath)
    print(example_storage.local_dirpath)
