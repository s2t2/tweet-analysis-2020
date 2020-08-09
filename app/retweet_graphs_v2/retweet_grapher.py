
import os
from datetime import datetime
import time

from memory_profiler import profile
from dotenv import load_dotenv
from networkx import DiGraph

from app import APP_ENV, DATA_DIR, SERVER_NAME, SERVER_DASHBOARD_URL
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import dt_to_s
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.email_service import send_email

load_dotenv()

USERS_LIMIT = os.getenv("USERS_LIMIT") # default is None
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="2500"))

class RetweetGrapher():

    def __init__(self, graph_storage, bq_service=None,
                        topic=None, tweets_start_at=None, tweets_end_at=None,
                        users_limit=USERS_LIMIT, batch_size=BATCH_SIZE):
        self.bq_service = bq_service or BigQueryService()
        self.graph_storage = graph_storage

        # CONVERSATION PARAMS

        self.topic = topic
        if self.topic:
            self.topic = self.topic.upper()

        self.tweets_start_at = tweets_start_at
        self.tweets_end_at = tweets_end_at

        # PROCESSING PARAMS

        self.users_limit = users_limit
        if self.users_limit:
            self.users_limit = int(self.users_limit)

        self.batch_size = int(batch_size)

        print("-------------------------")
        print("RETWEET GRAPHER...")
        print("  TOPIC:", self.topic)
        print("  TWEETS START:", self.tweets_start_at)
        print("  TWEETS END:", self.tweets_end_at)
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)

        self.start_at = None
        self.end_at = None
        self.duration_seconds = None
        self.counter = None
        self.results = None
        self.graph = None

    @property
    def metadata(self):
        return {
            "app_env": APP_ENV,
            "graph_storage": self.graph_storage.metadata,
            "bq_service": self.bq_service.metadata,
            "topic": self.topic,
            "tweets_start_at": dt_to_s(self.tweets_start_at),
            "tweets_end_at": dt_to_s(self.tweets_end_at),
            "users_limit": self.users_limit,
            "batch_size": self.batch_size
        }

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.start_at = time.perf_counter() # todo: let's use a real datetime string and add it to the metadata
        self.counter = 0 # represents the number of items processed

    @profile
    def perform(self):
        #self.save_metadata()
        #self.start()
        self.results = []
        self.graph = DiGraph()

        for row in self.bq_service.fetch_retweet_counts_in_batches(start_at=dt_to_s(self.tweets_start_at), end_at=dt_to_s(self.tweets_end_at)):

            self.graph.add_edge(
                row["user_screen_name"], # todo: user_id
                row["retweet_user_screen_name"], # todo: retweet_user_id
                weight=row["retweet_count"]
            )

            self.counter += 1
            if self.counter % self.batch_size == 0:
                rr = {
                    "ts": logstamp(),
                    "counter": self.counter,
                    "nodes": self.graph.number_of_nodes(),
                    "edges": self.graph.number_of_edges()
                }
                print(rr["ts"], "|", fmt_n(rr["counter"]), "|", fmt_n(rr["nodes"]), "|", fmt_n(rr["edges"]))
                self.results.append(rr)

                # gets us an approximate users limit but reached a fraction of the time (perhaps more performant when there are millions of rows)
                if self.users_limit and self.counter >= self.users_limit:
                    break

        #self.end()
        #self.report()
        #self.save_results()
        #self.save_graph()

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

    grapher = RetweetGrapher()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
