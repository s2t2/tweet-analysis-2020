
import os
#from pprint import pprint
#import random

from dotenv import load_dotenv
import numpy as np
from networkx import DiGraph

from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import dt_to_date, dt_to_s
from app.decorators.number_decorators import fmt_n
from app.bq_base_grapher import BigQueryBaseGrapher
from app.graph_storage_service import GraphStorageService

load_dotenv()

USERS_LIMIT=1000
#TWEETS_START_AT = os.getenv("TWEETS_START_AT", default="2019-12-15 00:00:00")
#TWEETS_END_AT = os.getenv("TWEETS_START_AT", default="2020-03-21 23:59:59")

class BigQueryWeeklyRetweetGrapher(BigQueryBaseGrapher):

    #def __init__(self, tweets_start_at=TWEETS_START_AT, tweets_end_at=TWEETS_END_AT):
    #    super().__init__()
    #    self.tweets_start_at = tweets_start_at
    #    self.tweets_end_at = tweets_end_at

    @property
    def metadata(self):
        return {**super().metadata, **{
            "retweeters":True,
            "conversation": {
                "topic": None,
                "start_at": self.tweets_start_at,
                "end_at": self.tweets_end_at,
            }
        }} # merges dicts

    def perform(self):
        print("--------------------")
        print("FETCHING WEEKS...")
        self.weeks = list(self.bq_service.fetch_retweet_weeks())

        print("--------------------")
        print("WEEKS:")
        for wk in self.weeks:
            wk_id = f"{wk.year}-{str(wk.week).zfill(2)}"
            print("   ", wk_id, f"('{dt_to_date(wk.min_created)}' - '{dt_to_date(wk.max_created)}')", "|",
                f"DAYS: {fmt_n(wk.day_count)}", "|",
                f"USERS: {fmt_n(wk.user_count)}", "|",
                f"RETWEETS: {fmt_n(wk.retweet_count)}"
             )

        print("--------------------")
        #row = random.choice(self.rows) # TODO: see which ones have not already been graphed, and take the first one
        wk = self.weeks[1] # TODO: see which ones have not already been graphed, and take the first one
        wk_id = f"{wk.year}-{str(wk.week).zfill(2)}"
        print("SELECTED WEEK:", wk_id)
        #pprint(dict(wk))

        seek_confirmation()

        #
        # INIT
        #

        self.storage_service = GraphStorageService(
            local_dirpath = os.path.join(DATA_DIR, "graphs", "weekly", wk_id),
            gcs_dirpath = os.path.join("storage", "data", "graphs", "weekly", wk_id)
        )

        self.tweets_start_at = dt_to_s(wk.min_created)
        self.tweets_end_at = dt_to_s(wk.max_created)
        self.users_limit = USERS_LIMIT

        #
        # PERFORMANCE
        #

        self.storage_service.write_metadata_to_file(self.metadata)
        self.storage_service.upload_metadata()

        self.start()
        self.results = []
        #self.edges = []
        self.graph = DiGraph()

        #counter = 0
        for row in self.bq_service.fetch_retweet_counts_in_batches(start_at=self.tweets_start_at, end_at=self.tweets_end_at):

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

            if self.users_limit and self.counter >= self.users_limit:
                break

        self.end()
        self.report()

        self.storage_service.write_results_to_file(self.results)
        self.storage_service.upload_results()

        self.storage_service.write_graph_to_file(self.graph)
        self.storage_service.upload_graph()



if __name__ == "__main__":

    grapher = BigQueryWeeklyRetweetGrapher()

    grapher.perform()
