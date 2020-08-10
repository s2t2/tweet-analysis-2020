
import os
import json
import pickle
from memory_profiler import profile
from pprint import pprint

from pandas import DataFrame
from networkx import write_gpickle, read_gpickle
from dotenv import load_dotenv

from conftest import compile_mock_rt_graph
from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.gcs_service import GoogleCloudStorageService
from conftest import compile_mock_rt_graph

load_dotenv()

DIRPATH = os.getenv("DIRPATH", default="graphs/mock_graph")

class GraphStorage:

    def __init__(self, dirpath=None, gcs_service=None):
        """
        Saves and loads artifacts from the networkx graph compilation process
            ...to and from local storage and/or Google Cloud Storage.

        Params:
            dirpath (str) like "graphs/my_graph/123"
        """
        self.gcs_service = gcs_service or GoogleCloudStorageService()

        self.dirpath = dirpath or DIRPATH
        self.gcs_dirpath = os.path.join("storage", "data", self.dirpath)
        self.local_dirpath = os.path.join(DATA_DIR, self.dirpath) # TODO: to make compatible on windows, split the dirpath on "/" and re-join using os.sep

        print("-------------------------")
        print("GRAPH STORAGE...")
        print("   DIRPATH:",  self.dirpath)
        print("   GCS DIRPATH:", self.gcs_dirpath)
        print("   LOCAL DIRPATH:", os.path.abspath(self.local_dirpath))

        seek_confirmation()

        if not os.path.exists(self.local_dirpath):
            os.makedirs(self.local_dirpath)

        self.results = None
        self.graph = None

    @property
    def metadata(self):
        return {
            "dirpath": self.dirpath,
            #"local_dirpath": os.path.abspath(self.local_dirpath),
            #"gcs_dirpath": self.gcs_dirpath,
            "gcs_service": self.gcs_service.metadata
        }

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
    def local_graph_filepath(self):
        return os.path.join(self.local_dirpath, "graph.gpickle")

    def write_metadata_to_file(self):
        print(logstamp(), "WRITING METADATA...")
        with open(self.local_metadata_filepath, "w") as f:
            json.dump(self.metadata, f)

    def write_results_to_file(self):
        print(logstamp(), "WRITING RESULTS...")
        df = DataFrame(self.results)
        df.index.name = "row_id"
        df.index = df.index + 1
        df.to_csv(self.local_results_filepath)

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
    def gcs_results_filepath(self):
        return os.path.join(self.gcs_dirpath, "results.csv")

    @property
    def gcs_graph_filepath(self):
        return os.path.join(self.gcs_dirpath, "graph.gpickle")

    def upload_metadata(self):
        print(logstamp(), "UPLOADING JOB METADATA...", self.gcs_metadata_filepath)
        blob = self.gcs_service.upload(self.local_metadata_filepath, self.gcs_metadata_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_results(self):
        print(logstamp(), "UPLOADING RESULTS...", self.gcs_results_filepath)
        blob = self.gcs_service.upload(self.local_results_filepath, self.gcs_results_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_graph(self):
        print(logstamp(), "UPLOADING GRAPH...", self.gcs_graph_filepath)
        blob = self.gcs_service.upload(self.local_graph_filepath, self.gcs_graph_filepath)
        print(logstamp(), blob)

    def download_graph(self):
        print(logstamp(), "DOWNLOADING GRAPH...", self.gcs_graph_filepath)
        self.gcs_service.download(self.gcs_graph_filepath, self.local_graph_filepath)

    #
    # CONVENIENCE METHODS
    #

    def save_metadata(self):
        self.write_metadata_to_file()
        self.upload_metadata()

    def save_results(self):
        self.write_results_to_file()
        self.upload_results()

    def save_graph(self):
        self.write_graph_to_file()
        self.upload_graph()

    #
    # GRAPH LOADING AND ANALYSIS
    #

    @profile
    def load_graph(self):
        """Assumes the graph already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_graph_filepath):
            self.download_graph()

        return self.read_graph_from_file()

    def report(self):
        if not self.graph:
            self.graph = self.load_graph()

        print("-------------------")
        print(type(self.graph))
        print("  NODES:", fmt_n(self.graph.number_of_nodes()))
        print("  EDGES:", fmt_n(self.graph.number_of_edges()))
        print("-------------------")

if __name__ == "__main__":

    storage = GraphStorage()

    storage.graph = compile_mock_rt_graph()
    storage.report()
    storage.write_graph_to_file()

    storage.graph = None
    storage.load_graph()
    storage.report()
