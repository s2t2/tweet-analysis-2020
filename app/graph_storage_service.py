
import os
import json
import pickle
from memory_profiler import profile

from pandas import DataFrame
from networkx import DiGraph, write_gpickle

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.gcs_service import GoogleCloudStorageService
from conftest import compile_mock_rt_graph

class GraphStorageService:

    def __init__(self, local_dirpath=None, gcs_dirpath=None, gcs_service=None):
        """
        Saves and loads artifacts from the networkx graph compilation process
            to local storage, and optionally to Google Cloud Storage.
            Graphs and other artifacts are external to this object.

        Params:
            local_dirpath (str) like "/Users/USERNAME/path/to/repo/data/graphs/2020-08-02-1818"
            gcs_dirpath (str) like "storage/data/graphs/2020-08-02-1818"
        """
        self.gcs_service = gcs_service or GoogleCloudStorageService()
        self.gcs_dirpath = gcs_dirpath or os.path.join("storage", "data", "graphs", "example")
        self.local_dirpath = local_dirpath or os.path.join(DATA_DIR, "graphs", "example")

        print("----------------------")
        print("GRAPH STORAGE...")
        print("   GCS DIR:", self.gcs_dirpath)
        print("   LOCAL DIR:", self.local_dirpath)
        print("----------------------")
        seek_confirmation()
        if not os.path.exists(self.local_dirpath):
            os.makedirs(self.local_dirpath)

        self.metadata = {}
        self.results = []
        self.edges = []
        self.graph = DiGraph()

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

    def write_metadata_to_file(self, metadata=None, metadata_filepath=None):
        """
        Params: metadata (dict)
        """
        print(logstamp(), "WRITING METADATA...")
        with open(metadata_filepath or self.local_metadata_filepath, "w") as f:
            json.dump(metadata or self.metadata, f)

    def write_results_to_file(self, results=None, results_filepath=None):
        """
        Params: results (list of dict)
        """
        print(logstamp(), "WRITING RESULTS...")
        df = DataFrame(results or self.results)
        df.to_csv(results_filepath or self.local_results_filepath)

    def write_edges_to_file(self, edges=None, edges_filepath=None):
        """
        Params: edges (list of dict)
        """
        print(logstamp(), "WRITING EDGES...:")
        with open(edges_filepath or self.local_edges_filepath, "wb") as f:
            pickle.dump(edges or self.edges, f)

    def write_graph_to_file(self, graph=None, graph_filepath=None):
        """
        Params: graph (DiGraph)
        """
        print(logstamp(), "WRITING GRAPH...")
        write_gpickle(graph or self.graph, graph_filepath or self.local_graph_filepath)

    def read_graph_from_file(self, graph_filepath=None):
        print(logstamp(), "READING GRAPH...")
        return read_gpickle(graph_filepath or self.local_graph_filepath)

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

    def download_graph(self):
        print(logstamp(), "DOWNLOADING GRAPH...", self.gcs_graph_filepath)
        self.gcs_service.download(self.gcs_graph_filepath, self.local_graph_filepath)
        print(logstamp(), blob)

    #
    # GRAPH LOADING AND ANALYSIS
    #

    @profile
    def load_graph(self):
        if not os.path.isfile(self.local_graph_filepath):
            self.download_graph()
        return self.read_graph_from_file()

if __name__ == "__main__":

    storage = GraphStorageService()

    storage.metadata = {"app_env": APP_ENV, "config": {"a":True, "b": 2500}}
    storage.write_metadata_to_file()
    storage.upload_metadata()

    storage.results = [
        {"ts": "2020-01-01 10:00:00", "counter": 2500, "nodes": 100_000, "edges": 150_000},
        {"ts": "2020-01-01 10:00:00", "counter": 5000, "nodes": 200_000, "edges": 400_000},
        {"ts": "2020-01-01 10:00:00", "counter": 7500, "nodes": 300_000, "edges": 900_000}
    ]
    storage.write_results_to_file()
    storage.upload_results()

    storage.graph = compile_mock_rt_graph()
    storage.write_graph_to_file()
    storage.upload_graph()
