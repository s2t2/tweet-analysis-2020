
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
from app.bq_service import BigQueryService
from app.graph_storage_service import GraphStorageService

load_dotenv()

WEEK_ID = os.getenv("WEEK_ID")


class Week:
    def __init__(self, row):
        """
        Param row (google.cloud.bigquery.table.Row) one of the weeks fetched from BigQuery
        """
        self.row = row

    @property
    def week_id(self):
        return f"{self.row.year}-{str(self.row.week).zfill(2)}" #> "2019-52", "2020-01", etc.

    @property
    def details(self):
        details = ""
        details += f"ID: {self.week_id} | "
        details += f"FROM: '{dt_to_date(self.row.min_created)}' "
        details += f"TO: '{dt_to_date(self.row.max_created)}' | "
        details += f"DAYS: {fmt_n(self.row.day_count)} | "
        details += f"USERS: {fmt_n(self.row.user_count)} | " + f"RETWEETS: {fmt_n(self.row.retweet_count)}"
        return details


class BigQueryWeeklyRetweetGrapher(BigQueryBaseGrapher):
    # takes 8 mins for 550 users
    # takes hours for lots of users.
    # needs to process each user X each user they retweeted, so edge counter will be larger than total retweeters

    def __init__(self, week_id=WEEK_ID):
        self.week_id = week_id

        print("--------------------")
        print("FETCHING WEEKS...")
        bq_service = BigQueryService()
        weeks = [Week(row) for row in list(bq_service.fetch_retweet_weeks())]
        for week in weeks:
            print("   ", week.details)

        print("--------------------")
        print("SELECTING A WEEK...")
        # TODO: see which ones have not already been graphed, and take the first one
        #row = random.choice(self.rows)
        #wk = self.weeks[1]
        selected_id = self.week_id or input("PLEASE SELECT A WEEK (E.G. '2019-52', '2020-01', ETC.): ")
        try:
            selected_week = [wk for wk in weeks if wk.week_id == selected_id][0]
        except IndexError as err:
            print("OOPS - PLEASE CHECK WEEK ID AND TRY AGAIN...")
            exit()

        #print("--------------------")
        #print("SETTING THE WEEK...")
        self.week_id = selected_id
        #print("ID:", self.week_id)
        self.week = selected_week
        #print("TOTAL USERS:", self.week.row.user_count)
        print("   ", self.week.details)
        self.tweets_start_at = self.week.row.min_created
        self.tweets_end_at = self.week.row.max_created
        #print("TWEETS START:", dt_to_date(self.tweets_start_at))
        #print("TWEETS END:", dt_to_date(self.tweets_end_at))

        seek_confirmation()

        storage_service = GraphStorageService(
            local_dirpath = os.path.join(DATA_DIR, "graphs", "weekly", self.week_id),
            gcs_dirpath = os.path.join("storage", "data", "graphs", "weekly", self.week_id)
        )
        #self.storage_service = storage_service
        super().__init__(bq_service=bq_service, storage_service=storage_service)

    @property
    def metadata(self):
        return {**super().metadata, **{
            "conversation": {
                "retweeters":True,
                "topic": None,
                "week_id": self.week_id,
                "tweets_start_at": dt_to_s(self.tweets_start_at), # string is serializeable
                "tweets_end_at": dt_to_s(self.tweets_end_at), # string is serializeable
            }
        }} # merges dicts

    @profile
    def perform(self):
        self.storage_service.write_metadata_to_file(self.metadata)
        self.storage_service.upload_metadata()

        self.start()
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

    grapher.send_completion_email(subject=f"[Tweet Analysis] Retweet Graph Complete! (WK {grapher.week_id})")

    grapher.sleep()
