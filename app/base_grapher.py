

from datetime import datetime

from app import APP_ENV, DATA_DIR
from app.graph_storage import GraphStorage

class BaseGrapher(GraphStorage):

    def __init__(self, job_id=None):
        self.job_id = (job_id or datetime.now().strftime("%Y-%m-%d-%H%M"))
        GraphStorage.__init__(
            local_dirpath = os.path.join(DATA_DIR, "graphs", job_id),
            gcs_dirpath = os.path.join("storage", "data", "graphs", job_id)
        )

    @property
    def metadata(self):
        return {"app_env": APP_ENV, "job_id": self.job_id}

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


if __name__ == "__main__":

    grapher = BaseGrapher()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
