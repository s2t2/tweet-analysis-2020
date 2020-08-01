
import os
import time
from functools import lru_cache

from networkx import read_gpickle, DiGraph
from dotenv import load_dotenv
from memory_profiler import profile

from app import DATA_DIR
from app.workers import fmt_n
from app.friend_graphs.base_grapher import BaseGrapher

load_dotenv()

JOB_ID = os.getenv("JOB_ID", default="2020-05-30-0338")
STORAGE_MODE = os.getenv("STORAGE_MODE", default="local")

class GraphAnalyzer():
    def __init__(self, job_id=JOB_ID, storage_mode=STORAGE_MODE):
        """
        Params:

            job_id (str) the identifier of a completed job which has produced a corresponding graph object

            storage_mode (str) where the graph object file has been stored ("local" or "remote")
        """
        self.storage_mode = storage_mode
        self.job_id = job_id
        self.job = BaseGrapher(job_id=self.job_id)

        self.local_dirpath = self.job.local_dirpath

    def __repr__(self):
        return f"<GraphAnalyzer {self.job_id}>"

    @property
    @lru_cache(maxsize=None) # memoizes the results
    def graph(self):
        return self.load_graph()

    #@profile
    def load_graph(self):
        if not os.path.isdir(self.job.local_dirpath):
            print("PREPARING LOCAL DOWNLOAD DIR...")
            os.mkdir(self.job.local_dirpath)

        if self.storage_mode == "local" or os.path.isfile(self.job.local_graph_filepath):
            print("LOADING GRAPH FROM LOCAL FILE...")
            return read_gpickle(self.job.local_graph_filepath)

        elif self.storage_mode == "remote":
            print("LOADING GRAPH FROM REMOTE STORAGE...")
            self.job.gcs_service.download(self.job.gcs_graph_filepath, self.job.local_graph_filepath)
            return read_gpickle(self.job.local_graph_filepath)

    def report(self):
        print("GRAPH:", type(self.graph))
        print("NODES:", fmt_n(len(self.graph.nodes))) # self.graph.number_of_nodes()
        print("EDGES:", fmt_n(len(self.graph.edges))) # self.graph.number_of_edges()
        #print("SIZE:", fmt_n(self.graph.size())) # same as edges

if __name__ == "__main__":

    analyzer = GraphAnalyzer()
    print(analyzer)

    analyzer.report()
