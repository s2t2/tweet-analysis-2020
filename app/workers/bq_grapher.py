
import os
import time

from networkx import DiGraph
from memory_profiler import profile

from app import APP_ENV
from app.bq_service import BigQueryService
from app.gcs_service import GoogleCloudStorageService
from app.workers import fmt_ts, fmt_n
from app.workers.base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    def __init__(self, bq_service=None, gcs_service=None):
        super().__init__()
        self.bq_service = (bq_service or BigQueryService.cautiously_initialized())
        self.gcs_service = (gcs_service or GoogleCloudStorageService())

        self.bucket = self.gcs_service.get_bucket()
        self.gcs_dirpath = os.path.join("storage", "data", self.job_id)
        self.gcs_metadata_filepath = os.path.join(self.gcs_dirpath, "metadata.json")
        self.gcs_results_filepath = os.path.join(self.gcs_dirpath, "results.csv")
        self.gcs_edges_filepath = os.path.join(self.gcs_dirpath, "edges.gpickle")
        self.gcs_graph_filepath = os.path.join(self.gcs_dirpath, "graph.gpickle")


    @property
    def metadata(self):
        return {"job_id": self.job_id,
                "dry_run": self.dry_run,
                "batch_size": self.batch_size,
                "bq_service": self.bq_service.metadata}

    @profile
    def perform(self):
        self.edges = None #[]
        self.graph = DiGraph()
        self.running_results = []

        for row in self.bq_service.fetch_user_friends_in_batches():
            self.counter += 1

            if not self.dry_run:
                self.graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])

            if self.counter % self.batch_size == 0:
                rr = {"ts": fmt_ts(), "counter": self.counter, "nodes": len(self.graph.nodes), "edges": len(self.graph.edges)}
                print(rr["ts"], "|", fmt_n(rr["counter"]), "|", fmt_n(rr["nodes"]), "|", fmt_n(rr["edges"]))
                self.running_results.append(rr)

    def upload_metadata(self):
        print(fmt_ts(), "UPLOADING JOB METADATA...", self.gcs_metadata_filepath)
        blob = self.bucket.blob(self.gcs_metadata_filepath)
        blob.upload_from_filename(self.local_metadata_filepath)
        print(blob)
        return blob

    def upload_results(self):
        print(fmt_ts(), "UPLOADING JOB RESULTS...", self.gcs_results_filepath)
        blob = self.bucket.blob(self.gcs_results_filepath)
        blob.upload_from_filename(self.local_results_filepath)
        print(blob)
        return blob

    def upload_edges(self):
        print(fmt_ts(), "UPLOADING NETWORK EDGES...", self.gcs_edges_filepath)
        blob = self.bucket.blob(self.gcs_edges_filepath)
        blob.upload_from_filename(self.local_edges_filepath)
        print(blob)
        return blob

    def upload_graph(self):
        print(fmt_ts(), "WRITING GRAPH...", self.gcs_graph_filepath)
        blob = self.bucket.blob(self.gcs_graph_filepath)
        blob.upload_from_filename(self.local_graph_filepath)
        print(blob)
        return blob

if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.write_metadata_to_file()
    grapher.upload_metadata()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
    grapher.write_results_to_file()
    grapher.upload_results()
    grapher.write_edges_to_file()
    grapher.upload_edges()
    grapher.write_graph_to_file()
    grapher.upload_graph()

    if APP_ENV == "production":
        time.sleep(12 * 60 * 60) # twelve hours
