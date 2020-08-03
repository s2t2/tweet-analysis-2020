
import os
#from pprint import pprint
#import random

from dotenv import load_dotenv
import numpy as np
from networkx import DiGraph
from memory_profiler import profile

from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import dt_to_date, dt_to_s, logstamp
from app.decorators.number_decorators import fmt_n
from app.bq_base_grapher import BigQueryBaseGrapher
from app.graph_storage_service import GraphStorageService

load_dotenv()

WEEK_ID = os.getenv("WEEK_ID")

#TWEETS_START_AT = os.getenv("TWEETS_START_AT", default="2019-12-15 00:00:00")
#TWEETS_END_AT = os.getenv("TWEETS_START_AT", default="2020-03-21 23:59:59")

def week_id(wk):
    return f"{wk.year}-{str(wk.week).zfill(2)}" #> "2019-52", "2020-01", etc.

def week_range(wk):
    return f"('{dt_to_date(wk.min_created)}' - '{dt_to_date(wk.max_created)}')"

#class Week():
#    def week_id(self):
#        return f"{self.year}-{str(self.week_num).zfill(2)}" #> "2019-52", "2020-01", etc.


class BigQueryWeeklyRetweetGrapher(BigQueryBaseGrapher):
    # takes 8 mins for 550 users
    # takes hours for lots of users.
    # needs to process each user X each user they retweeted, so edge counter will be larger than total retweeters

    #def __init__(self, tweets_start_at=TWEETS_START_AT, tweets_end_at=TWEETS_END_AT):
    #    super().__init__()
    #    self.tweets_start_at = tweets_start_at
    #    self.tweets_end_at = tweets_end_at

    @property
    def metadata(self):
        return {**super().metadata, **{
            "conversation": {
                "retweeters":True,
                "topic": None,
                "start_at": self.tweets_start_at,
                "end_at": self.tweets_end_at,
            }
        }} # merges dicts

    @profile
    def perform(self):
        print("--------------------")
        print("FETCHING WEEKS...")
        self.weeks = list(self.bq_service.fetch_retweet_weeks())

        print("--------------------")
        print("WEEKS:")
        for wk in self.weeks:
            print("   ", "ID: ", week_id(wk), week_range(wk), "|",
                f"DAYS: {fmt_n(wk.day_count)}", "|",
                f"USERS: {fmt_n(wk.user_count)}", "|",
                f"RETWEETS: {fmt_n(wk.retweet_count)}"
             )

        print("--------------------")
        print("SELECTED WEEK...")

        # TODO: see which ones have not already been graphed, and take the first one
        #row = random.choice(self.rows)
        #wk = self.weeks[1]
        selected_id = WEEK_ID or input("PLEASE SELECT A WEEK (E.G. '2019-52', '2020-01', ETC.): ")
        try:
            selected_week = [wk for wk in self.weeks if week_id(wk) == selected_id][0]
        except IndexError as err:
            print("OOPS - PLEASE CHECK WEEK ID AND TRY AGAIN...")
            exit()

        #wk_id = f"{wk.year}-{str(wk.week).zfill(2)}"
        print("ID:", selected_id)
        print("TOTAL USERS:", selected_week.user_count)
        #pprint(dict(wk))

        seek_confirmation()

        #
        # INIT
        #

        self.storage_service = GraphStorageService(
            local_dirpath = os.path.join(DATA_DIR, "graphs", "weekly", week_id(selected_week)),
            gcs_dirpath = os.path.join("storage", "data", "graphs", "weekly", week_id(selected_week))
        )

        self.tweets_start_at = dt_to_s(selected_week.min_created)
        self.tweets_end_at = dt_to_s(selected_week.max_created)
        if self.users_limit:
            self.users_limit = int(self.users_limit)

        #
        # PERFORMANCE
        #

        self.storage_service.write_metadata_to_file(self.metadata)
        self.storage_service.upload_metadata()

        self.start()
        self.results = []
        self.graph = DiGraph()

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

    grapher.sleep()
