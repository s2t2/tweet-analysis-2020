
import os
import pickle
import json
from pprint import pprint

from memory_profiler import profile

from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.file_storage import FileStorage


class ModelStorage(FileStorage):
    def  __init__(self, dirpath):
        super().__init__(dirpath=dirpath)

        self.local_metadata_filepath = os.path.join(self.local_dirpath, "metadata.json")
        self.gcs_metadata_filepath = os.path.join(self.gcs_dirpath, "metadata.json")

        self.local_graph_filepath = os.path.join(self.local_dirpath, "graph.gpickle")
        self.gcs_graph_filepath = os.path.join(self.gcs_dirpath, "graph.gpickle")

        self.local_subgraph_filepath = os.path.join(self.local_dirpath, "subgraph.gpickle")
        self.gcs_subgraph_filepath = os.path.join(self.gcs_dirpath, "subgraph.gpickle")


    #
    # LOCAL STORAGE
    #

    def write_model(self, model):
        print(logstamp(), "WRITING MODEL TO LOCAL FILE...")
        with open(self.local_model_filepath, "wb") as f:
            pickle.dump(model, f)

    def read_model(self):
        print(logstamp(), "READING MODEL FROM LOCAL FILE...")
        with open(self.local_model_filepath, "rb") as f:
            return pickle.load(f)

    def write_subgraph(self, subgraph):
        print(logstamp(), "WRITING subgraph TO LOCAL FILE...")
        with open(self.local_subgraph_filepath, "wb") as f:
            pickle.dump(subgraph, f)

    def read_subgraph(self):
        print(logstamp(), "READING subgraph FROM LOCAL FILE...")
        with open(self.local_subgraph_filepath, "rb") as f:
            return pickle.load(f)

    def write_metadata(self, metadata):
        print(logstamp(), "WRITING metadata TO LOCAL FILE...")
        with open(self.local_metadata_filepath, "w") as f:
            json.dump(metadata, f)

    #
    # REMOTE STORAGE
    #

    def upload_model(self):
        self.upload_file(self.local_model_filepath, self.gcs_model_filepath)

    def download_model(self):
        self.upload_file(self.gcs_model_filepath, self.local_model_filepath)

    def upload_subgraph(self):
        self.upload_file(self.local_subgraph_filepath, self.gcs_subgraph_filepath)

    def download_subgraph(self):
        self.upload_file(self.gcs_subgraph_filepath, self.local_subgraph_filepath)

    def upload_metadata(self):
        self.upload_file(self.local_metadata_filepath, self.gcs_metadata_filepath)

    #
    # CONVENIENCE METHODS
    #

    def save_model(self, model):
        self.write_model(model)
        if self.wifi:
            self.upload_model()

    @profile
    def load_model(self):
        """Assumes the model already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_model_filepath):
            self.download_model()
        return self.read_model()

    def save_subgraph(self, subgraph):
        self.write_subgraph(subgraph)
        if self.wifi:
            self.upload_subgraph()

    @profile
    def load_subgraph(self):
        """Assumes the subgraph already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_subgraph_filepath):
            self.download_subgraph()
        return self.read_subgraph()

    def save_metadata(self, metadata):
        self.write_metadata(metadata)
        if self.wifi:
            self.upload_metadata()


if __name__ == "__main__":

    storage = DailyFriendGraphStorage()
