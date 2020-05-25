
import os

from networkx import DiGraph
from memory_profiler import profile

from app.bq_service import BigQueryService
#from app.gcs_service import GoogleCloudStorageService
from app.workers import fmt_ts, fmt_n
from app.workers.base_grapher import BaseGrapher

class Grapher(BaseGrapher):

    def __init__(self, bq_service=None):
        super().__init__()
        self.bq_service = (bq_service or BigQueryService.cautiously_initialized())

        self.gcs_dirpath = os.path.join("storage", "data", self.job_id)
        self.results_filepath  = os.path.join(self.gcs_dirpath, "results.csv")
        self.edges_filepath = os.path.join(self.gcs_dirpath, "edges.gpickle")
        self.graph_filepath = os.path.join(self.gcs_dirpath, "graph.gpickle")

    @profile
    def perform(self):
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

    def upload_results(self):
        print(fmt_ts(), "WRITING RESULTS...")
        #DataFrame(self.running_results).to_csv(csv_filepath)

    def upload_edges(self):
        print(fmt_ts(), "WRITING EDGES...:")
        #with open(edges_filepath, "wb") as pickle_file:
        #    pickle.dump(self.edges, pickle_file)

    def upload_graph(self):
        print(fmt_ts(), "WRITING GRAPH...")
        #write_gpickle(self.graph, self.graph_filepath)

if __name__ == "__main__":

    grapher = Grapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
    grapher.upload_results()
    grapher.upload_edges()
    grapher.upload_graph()
