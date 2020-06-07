
import os

from networkx import read_gpickle
from dotenv import load_dotenv

from app import DATA_DIR

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

    def load_graph(self):
        return read_gpickle(self.graph_filepath)

    def report(self, graph=None):
        if not graph:
            graph = self.load_graph()
        print("NODES:", fmt_n(len(self.graph.nodes)))
        print("EDGES:", fmt_n(len(self.graph.edges)))
        print("SIZE:", fmt_n(self.graph.size()))

if __name__ == "__main__":

    analyzer = LocalGraphAnalyzer(job_id=JOB_ID)
    print(type(analyzer))

    graph = analyzer.load_graph()

    analyzer.report(graph)
