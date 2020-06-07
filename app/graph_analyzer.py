
import os
import time
from functools import lru_cache

from networkx import read_gpickle, DiGraph
from dotenv import load_dotenv

from app import DATA_DIR
from app.workers import fmt_n
from app.workers.base_grapher

load_dotenv()

JOB_ID = os.getenv("JOB_ID", default="2020-05-30-0338")

class GraphAnalyzer():
    def __init__(self, job_id, storage_mode="local"):
        """
        Params:

            job_id (str) the identifier of a completed job which has produced a corresponding graph object

            storage_mode (str) where the graph object file has been stored ("local" or "remote")
        """
        self.storage_mode = storage_mode
        self.job_id = job_id
        self.job = BaseGrapher(job_id=self.job_id)

    def __repr__(self):
        return f"<GraphAnalyzer {self.job_id}>"

    @property
    @lru_cache(maxsize=None) # memoizes the results
    def graph(self):
        return self.load_graph()

    def load_graph(self):
        if self.storage_mode == "local":
            print("LOADING GRAPH FROM LOCAL FILE...")
            return read_gpickle(self.job.local_graph_filepath)

        elif self.storage_mode == "remote":
            print("LOADING GRAPH FROM REMOTE STORAGE...")
            breakpoint()
            #TODO: job.gcs_service.download(self.job.gcs_graph_filepath, self.job.local_graph_filepath)
            return read_gpickle(self.job.local_graph_filepath)

    def report(self, graph=None):
        if not isinstance(graph, DiGraph):
            graph = self.load_graph()
        print("GRAPH:", type(graph))
        print("NODES:", fmt_n(len(graph.nodes)))
        print("EDGES:", fmt_n(len(graph.edges)))
        print("SIZE:", fmt_n(graph.size()))

if __name__ == "__main__":

    analyzer = LocalGraphAnalyzer(job_id=JOB_ID)
    print(analyzer)

    graph = DiGraph() #analyzer.load_graph()

    analyzer.report(graph)
