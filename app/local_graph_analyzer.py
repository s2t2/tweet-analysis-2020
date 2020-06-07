
import os
import time
from functools import lru_cache

from networkx import read_gpickle, DiGraph
from dotenv import load_dotenv

from app import DATA_DIR
from app.workers import fmt_n

load_dotenv()

JOB_ID = os.getenv("JOB_ID", default="2020-05-30-0338")

class LocalGraphAnalyzer():
    def __init__(self, job_id):
        """Params job_id (str) the identifier of a completed job which has produced a corresponding graph object"""
        self.job_id = job_id

        # TODO: refactor this functionality from BaseGrapher into a new GraphManager class
        self.dirpath = os.path.join(DATA_DIR, self.job_id)
        self.metadata_filepath = os.path.join(self.dirpath, "metadata.json")
        self.results_filepath = os.path.join(self.dirpath, "results.csv")
        self.edges_filepath = os.path.join(self.dirpath, "edges.gpickle")
        self.graph_filepath = os.path.join(self.dirpath, "graph.gpickle")
        if not os.path.exists(self.dirpath):
            raise "OOPS EXPECTING SOME GRAPH FILES AT..." + os.path.abspath(self.dirpath)

    def __repr__(self):
        return f"<LocalGraphAnalyzer {self.job_id} {os.path.exists(self.dirpath)}>"

    def load_graph(self):
        print("LOADING GRAPH FROM...", self.graph_filepath)
        return read_gpickle(self.graph_filepath)

    @lru_cache(maxsize=None) # memoizes the results
    def graph(self):
        return self.load_graph()

    @lru_cache(maxsize=None) # memoizes the results
    def test_method(self):
        print("DOING WORK HERE...")
        time.sleep(10)
        return "COMPLETE"

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

    # h/t: http://codingnews.info/post/memoization.html
    #  ... https://docs.python.org/3/library/functools.html#functools.lru_cache
    print(analyzer.test_method())
    print(analyzer.test_method())
    print(analyzer.test_method())
    print(analyzer.test_method())
    print(analyzer.test_method())
    print(analyzer.test_method())
    print(analyzer.test_method())
