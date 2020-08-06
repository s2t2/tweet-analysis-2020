




import os
import json
import pickle
from memory_profiler import profile

#from pandas import DataFrame
from networkx import write_gpickle, read_gpickle

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.gcs_service import GoogleCloudStorageService
from conftest import compile_mock_rt_graph

class GraphStorageService:

    def __init__(self, local_dirpath=None, gcs_service=None):
        """
        Saves and loads artifacts from the networkx graph compilation process to local storage, and optionally to Google Cloud Storage.

        Params:
            local_dirpath (str) somewhere in the data dir, like:
                "/Users/USERNAME/path/to/repo/data/graphs/2020-08-02-1818"
                "data/graphs/2020-08-02-1818"
                "data/graphs/weekly/2020-12"
        """
        self.local_dirpath = local_dirpath or os.path.join(DATA_DIR, "graphs", "example")
        self.gcs_dirpath = self.compile_gcs_dirpath(self.local_dirpath)
        self.gcs_service = gcs_service or GoogleCloudStorageService()

        print("----------------------")
        print("GRAPH STORAGE...")
        print("   GCS DIR:", self.gcs_dirpath)
        print("   LOCAL DIR:", self.local_dirpath)
        print("----------------------")

        seek_confirmation()
        self.make_local_dir()

    def compile_gcs_dirpath(self, local_dirpath):
        """
        Based on local directory path, compiles a corresponding directory on Google Cloud Storage.
            local_dirpath (str or path-like) "/Users/USERNAME/path/to/repo/data/graphs/2020-08-02-1818"
            gcs_dirpath (str) "storage/data/graphs/2020-08-02-1818"
        """
        stem = local_dirpath.split("data")[-1] #> '/graphs/example'
        return "storage/data" + stem #> "storage/data/graphs/example"

    def make_local_dir(self):
        if not os.path.exists(self.local_dirpath):
            os.makedirs(self.local_dirpath)

    #
    # LOCAL STORAGE
    #

    @property
    def local_metadata_filepath(self):
        return os.path.join(self.local_dirpath, "metadata.json")

    @property
    def local_graph_filepath(self):
        return os.path.join(self.local_dirpath, "graph.gpickle")

    def write_metadata_to_file(self):
        print(logstamp(), "WRITING METADATA...")
        with open(self.local_metadata_filepath, "w") as f:
            json.dump(self.metadata, f)

    def write_graph_to_file(self):
        print(logstamp(), "WRITING GRAPH...")
        write_gpickle(self.graph, self.local_graph_filepath)

    def read_graph_from_file(self):
        print(logstamp(), "READING GRAPH...")
        return read_gpickle(self.local_graph_filepath)

    #
    # REMOTE STORAGE
    #

    @property
    def gcs_metadata_filepath(self):
        return os.path.join(self.gcs_dirpath, "metadata.json")

    @property
    def gcs_graph_filepath(self):
        return os.path.join(self.gcs_dirpath, "graph.gpickle")

    def upload_metadata(self):
        print(logstamp(), "UPLOADING JOB METADATA...", self.gcs_metadata_filepath)
        blob = self.gcs_service.upload(self.local_metadata_filepath, self.gcs_metadata_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_graph(self):
        print(logstamp(), "UPLOADING GRAPH...", self.gcs_graph_filepath)
        blob = self.gcs_service.upload(self.local_graph_filepath, self.gcs_graph_filepath)
        print(logstamp(), blob)

    def download_graph(self):
        print(logstamp(), "DOWNLOADING GRAPH...", self.gcs_graph_filepath)
        self.gcs_service.download(self.gcs_graph_filepath, self.local_graph_filepath)

    #
    # GRAPH LOADING AND ANALYSIS
    #

    @profile
    def load_graph(self):
        """Assumes the graph already exists and is saved either locally or remotely"""
        if not os.path.isfile(self.local_graph_filepath):
            self.graph = self.download_graph()
        else:
            self.graph = self.read_graph_from_file()

    def report(self):
        print("-------------------")
        print(type(self.graph))
        print("  NODES:", fmt_n(self.graph.number_of_nodes()))
        print("  EDGES:", fmt_n(self.graph.number_of_edges()))
        print("-------------------")

if __name__ == "__main__":

    storage = GraphStorage()

    storage.metadata = {"app_env": APP_ENV, "config": {"a":True, "b": 2500}}
    storage.write_metadata_to_file()
    storage.upload_metadata()

    storage.graph = compile_mock_rt_graph()
    storage.report()
    storage.write_graph_to_file()
    storage.upload_graph()
