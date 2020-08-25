
import os
from datetime import datetime
import time

from memory_profiler import profile
from dotenv import load_dotenv
from networkx import DiGraph

from conftest import compile_mock_rt_graph
from app import APP_ENV, DATA_DIR, SERVER_NAME, SERVER_DASHBOARD_URL, seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import dt_to_s, logstamp
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.job import Job
#from app.email_service import send_email

load_dotenv()

TOPIC = os.getenv("TOPIC") # default is None
USERS_LIMIT = os.getenv("USERS_LIMIT") # default is None
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25000")) # it doesn't refer to the size of the batches fetched from BQ but rather the interval at which to take a reporting snapshot, which gets compiled and written to CSV. set this to a very large number like 25000 to keep memory costs down, if that's a concern for you.
TWEETS_START_AT = os.getenv("TWEETS_START_AT") # default is None
TWEETS_END_AT = os.getenv("TWEETS_END_AT") # default is None

DRY_RUN = (os.getenv("DRY_RUN", default="false") == "true")

class RetweetGrapher(GraphStorage, Job):

    def __init__(self, topic=TOPIC, tweets_start_at=TWEETS_START_AT, tweets_end_at=TWEETS_END_AT,
                        users_limit=USERS_LIMIT, batch_size=BATCH_SIZE,
                        storage_dirpath=None, bq_service=None):

        Job.__init__(self)
        GraphStorage.__init__(self, dirpath=storage_dirpath)
        self.bq_service = bq_service or BigQueryService()
        self.fetch_edges = self.bq_service.fetch_retweet_edges_in_batches_v2 # just being less verbose. feels like javascript

        # CONVERSATION PARAMS (OPTIONAL)

        self.topic = topic
        self.tweets_start_at = tweets_start_at
        self.tweets_end_at = tweets_end_at

        # PROCESSING PARAMS

        self.users_limit = users_limit
        if self.users_limit:
            self.users_limit = int(self.users_limit)

        self.batch_size = int(batch_size)

        print("-------------------------")
        print("RETWEET GRAPHER...")
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)
        print("  DRY RUN:", DRY_RUN)
        print("-------------------------")
        print("CONVERSATION PARAMS...")
        print("  TOPIC:", self.topic)
        print("  TWEETS START:", self.tweets_start_at)
        print("  TWEETS END:", self.tweets_end_at)

        seek_confirmation()

    @property
    def metadata(self):
        return {
            "app_env": APP_ENV,
            "storage_dirpath": self.dirpath,
            "bq_service": self.bq_service.metadata,
            "topic": self.topic,
            "tweets_start_at": str(self.tweets_start_at),
            "tweets_end_at": str(self.tweets_end_at),
            "users_limit": self.users_limit,
            "batch_size": self.batch_size
        }

    @profile
    def perform(self):
        self.results = []
        self.graph = DiGraph()

        for row in self.fetch_edges(topic=self.topic, start_at=self.tweets_start_at, end_at=self.tweets_end_at):

            self.graph.add_edge(row["user_id"], row["retweeted_user_id"], weight=row["retweet_count"])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.results.append(self.running_results)
                if self.users_limit and self.counter >= self.users_limit:
                    break

    @property
    def running_results(self):
        rr = {"ts": logstamp(),
            "counter": self.counter,
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges()
        }
        print(rr["ts"], "|", fmt_n(rr["counter"]), "|", fmt_n(rr["nodes"]), "|", fmt_n(rr["edges"]))
        return rr

if __name__ == "__main__":

    grapher = RetweetGrapher()
    grapher.save_metadata()
    grapher.start()

    if DRY_RUN:
        grapher.counter = 7500
        grapher.results = [
            {"ts": "2020-01-01 10:00:00", "counter": 2500, "nodes": 100_000, "edges": 150_000},
            {"ts": "2020-01-01 10:00:00", "counter": 5000, "nodes": 200_000, "edges": 400_000},
            {"ts": "2020-01-01 10:00:00", "counter": 7500, "nodes": 300_000, "edges": 900_000}
        ]
        grapher.graph = compile_mock_rt_graph()
    else:
        grapher.perform()

    grapher.end()
    grapher.report()
    grapher.save_results()
    grapher.save_graph()
