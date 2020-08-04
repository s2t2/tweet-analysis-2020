
import os
from datetime import datetime
import time

from dotenv import load_dotenv
from networkx import DiGraph

from app import APP_ENV, DATA_DIR, SERVER_NAME, SERVER_DASHBOARD_URL
from app.decorators.number_decorators import fmt_n
from app.graph_storage_service import GraphStorageService
from app.email_service import send_email

load_dotenv()

USERS_LIMIT = os.getenv("USERS_LIMIT") # default is None
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="2500"))

class BaseGrapher():

    def __init__(self, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE, storage_service=None):
        #self.job_id = datetime.now().strftime("%Y-%m-%d-%H%M")
        self.users_limit = users_limit
        self.batch_size = batch_size
        self.storage_service = storage_service or GraphStorageService()

        print("-----------------")
        print("BASE GRAPHER...")
        #print("  JOB ID:", self.job_id)
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)

        self.start_at = None
        self.counter = None

        self.results = None
        self.edges = None
        self.graph = None

        self.end_at = None
        self.duration_seconds = None



    @property
    def metadata(self):
        return {"app_env": APP_ENV, "users_limit": self.users_limit, "batch_size": self.batch_size}

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.start_at = time.perf_counter() # todo: let's use a real datetime string and add it to the metadata
        self.counter = 0 # represents the number of items processed

    def perform(self):
        """To be overridden by child class. Only the graph is required."""
        self.results = []
        #self.edges = []
        self.graph = DiGraph()

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.end_at = time.perf_counter() # todo: let's use a real datetime string and add it to the metadata
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {fmt_n(self.counter)} ITEMS IN {fmt_n(self.duration_seconds)} SECONDS")

    def save_metadata(self):
        self.storage_service.write_metadata_to_file(self.metadata)
        self.storage_service.upload_metadata()

    def save_results(self):
        self.storage_service.write_results_to_file(self.results)
        self.storage_service.upload_results()

    #def save_edges(self):
    #    self.storage_service.write_edges_to_file(self.edges)
    #    self.storage_service.upload_edges()

    def save_graph(self):
        self.storage_service.write_graph_to_file(self.graph)
        self.storage_service.upload_graph()

    def report(self):
        self.storage_service.report(self.graph)

    def send_completion_email(self, subject="[Tweet Analyzer] Graph Complete!"):
        if APP_ENV == "production":
            html = f"""
                <h3>Nice!</h3>
                <p>Server '{SERVER_NAME}' has completed its work.</p>
                <p>So please shut it off so it can get some rest.</p>
                <p>
                    <a href='{SERVER_DASHBOARD_URL}'>{SERVER_DASHBOARD_URL}</a>
                </p>
                <p>Thanks!</p>
            """
            response = send_email(subject, html)
            return response

    def sleep(self):
        if APP_ENV == "production":
            print("SLEEPING...")
            time.sleep(6 * 60 * 60) # six hours, more than enough time to stop the server


if __name__ == "__main__":

    grapher = BaseGrapher()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
