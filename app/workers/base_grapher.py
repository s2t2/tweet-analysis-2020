
import time
import os
from datetime import datetime as dt
import pickle
import json

from networkx import DiGraph, write_gpickle
from pandas import DataFrame

from app import APP_ENV, DATA_DIR
from app.workers import BATCH_SIZE, DRY_RUN, USERS_LIMIT, fmt_ts, fmt_n
from app.gcs_service import GoogleCloudStorageService

class BaseGrapher():
    """
    Example:
        grapher = BaseGrapher.cautiously_initialized()
        grapher.start()
        grapher.perform()
        grapher.end()
        grapher.report()
    """

    def __init__(self, dry_run=DRY_RUN, batch_size=BATCH_SIZE, users_limit=USERS_LIMIT, gcs_service=None):
        self.job_id = dt.now().strftime("%Y-%m-%d-%H%M") # a timestamp-based unique identifier, should be able to be included in a filepath, associates multiple files produced by the job with each other
        self.dry_run = (dry_run == True)
        self.batch_size = batch_size
        if users_limit:
            self.users_limit = int(users_limit)
        else:
            self.users_limit = None

        self.local_dirpath = os.path.join(DATA_DIR, self.job_id)
        if not os.path.exists(self.local_dirpath):
            os.mkdir(self.local_dirpath)
        self.local_metadata_filepath = os.path.join(self.local_dirpath, "metadata.json")
        self.local_results_filepath = os.path.join(self.local_dirpath, "results.csv")
        self.local_edges_filepath = os.path.join(self.local_dirpath, "edges.gpickle")
        self.local_graph_filepath = os.path.join(self.local_dirpath, "graph.gpickle")

        self.gcs_service = (gcs_service or GoogleCloudStorageService())
        self.gcs_dirpath = os.path.join("storage", "data", self.job_id)
        self.gcs_metadata_filepath = os.path.join(self.gcs_dirpath, "metadata.json")
        self.gcs_results_filepath = os.path.join(self.gcs_dirpath, "results.csv")
        self.gcs_edges_filepath = os.path.join(self.gcs_dirpath, "edges.gpickle")
        self.gcs_graph_filepath = os.path.join(self.gcs_dirpath, "graph.gpickle")

    @classmethod
    def cautiously_initialized(cls):
        service = cls()
        print("-------------------------")
        print("NETWORK GRAPHER CONFIG...")
        print("  JOB ID:", service.job_id)
        print("  DRY RUN:", str(service.dry_run).upper())
        print("  BATCH SIZE:", str(service.batch_size).upper())
        print("  USERS LIMIT:", service.users_limit)
        print("-------------------------")
        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        return service

    @property
    def metadata(self):
        return {"app_env": APP_ENV, "job_id": self.job_id, "dry_run": self.dry_run, "batch_size": self.batch_size}

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.start_at = time.perf_counter()
        self.counter = 0

    def perform(self):
        """To be overridden by child class"""
        self.graph = DiGraph()

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {fmt_n(self.counter)} USERS IN {fmt_n(self.duration_seconds)} SECONDS")

    def report(self):
        print("NODES:", fmt_n(len(self.graph.nodes)))
        print("EDGES:", fmt_n(len(self.graph.edges)))
        print("SIZE:", fmt_n(self.graph.size()))

    def write_metadata_to_file(self):
        print(fmt_ts(), "WRITING METADATA...")
        with open(self.local_metadata_filepath, "w") as metadata_file:
            json.dump(self.metadata, metadata_file)

    def write_results_to_file(self):
        print(fmt_ts(), "WRITING RESULTS...")
        df = DataFrame(self.running_results)
        df.to_csv(self.local_results_filepath)

    def write_edges_to_file(self):
        print(fmt_ts(), "WRITING EDGES...:")
        with open(self.local_edges_filepath, "wb") as pickle_file:
            pickle.dump(self.graph.edges, pickle_file)

    def write_graph_to_file(self):
        print(fmt_ts(), "WRITING GRAPH...")
        write_gpickle(self.graph, self.local_graph_filepath)

    def upload_metadata(self):
        print(fmt_ts(), "UPLOADING JOB METADATA...", self.gcs_metadata_filepath)
        blob = self.gcs_service.upload(self.local_metadata_filepath, self.gcs_metadata_filepath)
        print(fmt_ts(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_results(self):
        print(fmt_ts(), "UPLOADING JOB RESULTS...", self.gcs_results_filepath)
        blob = self.gcs_service.upload(self.local_results_filepath, self.gcs_results_filepath)
        print(fmt_ts(), blob) #> <Blob: impeachment-analysis-2020, storage/data/2020-05-26-0002/metadata.json, 1590465770194318>

    def upload_edges(self):
        print(fmt_ts(), "UPLOADING NETWORK EDGES...", self.gcs_edges_filepath)
        blob = self.gcs_service.upload(self.local_edges_filepath, self.gcs_edges_filepath)
        print(fmt_ts(), blob)

    def upload_graph(self):
        print(fmt_ts(), "WRITING GRAPH...", self.gcs_graph_filepath)
        blob = self.gcs_service.upload(self.local_graph_filepath, self.gcs_graph_filepath)
        print(fmt_ts(), blob)

if __name__ == "__main__":

    grapher = BaseGrapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
