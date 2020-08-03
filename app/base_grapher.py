
import os
from datetime import datetime
import time

from dotenv import load_dotenv
from networkx import DiGraph

from app import APP_ENV, DATA_DIR
from app.decorators.number_decorators import fmt_n
from app.graph_storage_service import GraphStorageService

load_dotenv()

USERS_LIMIT = os.getenv("USERS_LIMIT") # default is None
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=2500))

class BaseGrapher():

    def __init__(self, job_id=None, storage_service=None, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE):
        self.job_id = (job_id or datetime.now().strftime("%Y-%m-%d-%H%M"))
        self.storage_service = storage_service or GraphStorageService(
            local_dirpath=os.path.join(DATA_DIR, "graphs", self.job_id),
            gcs_dirpath=os.path.join("storage", "data", "graphs", self.job_id)
        )

        self.users_limit = users_limit
        self.batch_size = batch_size

        print("-----------------")
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)

    @property
    def metadata(self):
        return {"app_env": APP_ENV, "job_id": self.job_id, "users_limit": self.users_limit, "batch_size": self.batch_size}

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
        #if not self.graph:
        #    self.graph = self.storage_service.load_graph()

        print("-----------------")
        print("NODES:", fmt_n(self.graph.number_of_nodes()))
        print("EDGES:", fmt_n(self.graph.number_of_edges()))

    def sleep(self):
        if APP_ENV == "production":
            print("SLEEPING...")
            time.sleep(3 * 60 * 60) # three hours, more than enough time to stop the server


if __name__ == "__main__":

    grapher = BaseGrapher()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()

    grapher.sleep()
