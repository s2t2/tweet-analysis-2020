
import os
import json
import pickle
from memory_profiler import profile

from pandas import DataFrame
from networkx import DiGraph, write_gpickle

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.gcs_service import GoogleCloudStorageService

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

    def write_metadata_to_file(self, metadata, metadata_filepath=None):
        """
        Params: metadata (dict)
        """
        metadata_filepath = metadata_filepath or self.local_metadata_filepath
        print(logstamp(), "WRITING METADATA...")
        with open(metadata_filepath, "w") as metadata_file:
            json.dump(metadata, metadata_file)

    def write_results_to_file(self, job_results, results_filepath=None):
        """
        Params: job_results (list of dict)
        """
        results_filepath = results_filepath or self.local_results_filepath
        print(logstamp(), "WRITING RESULTS...")
        df = DataFrame(job_results)
        df.to_csv(results_filepath)

    def write_edges_to_file(self, edges, edges_filepath=None):
        """
        Params: edges (list of dict)
        """
        edges_filepath = edges_filepath or self.local_edges_filepath
        print(logstamp(), "WRITING EDGES...:")
        with open(edges_filepath, "wb") as pickle_file:
            pickle.dump(edges, pickle_file)

    def write_graph_to_file(self, graph, graph_filepath=None):
        """
        Params: graph (DiGraph)
        """
        graph_filepath = graph_filepath or self.local_graph_filepath
        print(logstamp(), "WRITING GRAPH...")
        write_gpickle(graph, graph_filepath)

    def read_graph_from_file(self, graph_filepath=None):
        graph_filepath = graph_filepath or self.local_graph_filepath
        print(logstamp(), "READING GRAPH...")
        return read_gpickle(graph_filepath)

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

    example_storage = GraphStorageService()

    print(example_storage.gcs_dirpath)
    print(example_storage.local_dirpath)
