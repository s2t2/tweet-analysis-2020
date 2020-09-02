
import os
import json
import pickle
from sys import getsizeof
from memory_profiler import profile #, memory_usage
from pprint import pprint

from pandas import DataFrame, read_csv
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

DRY_RUN = (os.getenv("DRY_RUN", default="false") == "true")

WIFI_ENABLED = (os.getenv("WIFI_ENABLED", default="true") == "true")

class GraphStorage:

    def __init__(self, dirpath=None, gcs_service=None):
        """
        Saves and loads artifacts from the networkx graph compilation process, using local storage and/or Google Cloud Storage.

        Params:
            dirpath (str) like "graphs/my_graph/123"

        TODO: bot probability stuff only apples to bot retweet graphs, and should probably be moved into a child graph storage class
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
        print("   WIFI ENABLED:", WIFI_ENABLED)

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
            "gcs_service": self.gcs_service.metadata,
            "wifi_enabled": WIFI_ENABLED
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

    @property
    def local_bot_probabilities_filepath(self):
        return os.path.join(self.local_dirpath, "bot_probabilities.csv")

    @property
    def local_bot_probabilities_histogram_filepath(self):
        return os.path.join(self.local_dirpath, "bot_probabilities_histogram.png")

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

    def read_bot_probabilities_from_file(self):
        print(logstamp(), "READING BOT PROBABILITIES CSV...")
        return read_csv(self.local_bot_probabilities_filepath)

    #
    # REMOTE STORAGE
    #

    def upload_file(self, local_filepath, remote_filepath):
        print(logstamp(), "UPLOADING FILE...", os.path.abspath(local_filepath))
        blob = self.gcs_service.upload(local_filepath, remote_filepath)
        print(logstamp(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def download_file(self, remote_filepath, local_filepath):
        print(logstamp(), "DOWNLOADING FILE...", remote_filepath)
        self.gcs_service.download(remote_filepath, local_filepath)

    @property
    def gcs_metadata_filepath(self):
        return os.path.join(self.gcs_dirpath, "metadata.json")

    @property
    def gcs_results_filepath(self):
        return os.path.join(self.gcs_dirpath, "results.csv")

    @property
    def gcs_graph_filepath(self):
        return os.path.join(self.gcs_dirpath, "graph.gpickle")

    @property
    def gcs_bot_probabilities_filepath(self):
        return os.path.join(self.gcs_dirpath, "bot_probabilities.csv")

    @property
    def gcs_bot_probabilities_histogram_filepath(self):
        return os.path.join(self.gcs_dirpath, "bot_probabilities_histogram.png")

    def upload_metadata(self):
        self.upload_file(self.local_metadata_filepath, self.gcs_metadata_filepath)

    def upload_results(self):
        self.upload_file(self.local_results_filepath, self.gcs_results_filepath)

    def upload_graph(self):
        self.upload_file(self.local_graph_filepath, self.gcs_graph_filepath)

    def upload_bot_probabilities(self):
        self.upload_file(self.local_bot_probabilities_filepath, self.gcs_bot_probabilities_filepath)

    def upload_bot_probabilities_histogram(self):
        self.upload_file(self.local_bot_probabilities_histogram_filepath, self.gcs_bot_probabilities_histogram_filepath)

    def download_graph(self):
        self.download_file(self.gcs_graph_filepath, self.local_graph_filepath)

    def download_bot_probabilities(self):
        self.download_file(self.gcs_bot_probabilities_filepath, self.local_bot_probabilities_filepath)

    def download_bot_probabilities_histogram(self):
        self.download_file(self.gcs_bot_probabilities_histogram_filepath, self.local_bot_probabilities_histogram_filepath)

    #
    # CONVENIENCE METHODS
    #

    def save_metadata(self):
        self.write_metadata_to_file()
        if WIFI_ENABLED:
            self.upload_metadata()

    def save_results(self):
        self.write_results_to_file()
        if WIFI_ENABLED:
            self.upload_results()

    def save_graph(self):
        self.write_graph_to_file()
        if WIFI_ENABLED:
            self.upload_graph()

    #
    # LOADING AND ANALYSIS
    #

    @profile
    def load_bot_probabilities(self):
        """Assumes the CSV file already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_bot_probabilities_filepath):
            self.download_bot_probabilities()

        return self.read_bot_probabilities_from_file()

    @profile
    def load_graph(self):
        """Assumes the graph already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_graph_filepath):
            self.download_graph()

        return self.read_graph_from_file()

    @property
    def node_count(self):
        return self.graph.number_of_nodes()

    @property
    def edge_count(self):
        return self.graph.number_of_edges()

    def report(self):
        if not self.graph:
            self.graph = self.load_graph()

        print("-------------------")
        print(type(self.graph))
        print("  NODES:", fmt_n(self.node_count))
        print("  EDGES:", fmt_n(self.edge_count))
        print("-------------------")

    @property
    def memory_report(self):
        if not self.graph:
            self.graph = self.load_graph()

        #memory_load = memory_usage(self.read_graph_from_file, interval=.2, timeout=1)
        file_size = os.path.getsize(self.local_graph_filepath) # in bytes
        print("-------------------")
        print(type(self.graph))
        print("  NODES:", fmt_n(self.node_count))
        print("  EDGES:", fmt_n(self.edge_count))
        print("  FILE SIZE:", fmt_n(file_size))
        print("-------------------")

        return {"nodes": self.node_count, "edges": self.edge_count, "file_size": file_size}

    #@property
    #def graph_metadata(self):
    #    return {"nodes": self.node_count, "edges": self.edge_count}

if __name__ == "__main__":

    storage = GraphStorage()

    if DRY_RUN:
        storage.graph = compile_mock_rt_graph()
        storage.report()
        storage.write_graph_to_file()
        storage.graph = None

    storage.load_graph()
    storage.report()
