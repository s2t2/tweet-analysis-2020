
import os
from pprint import pprint
#import random

from dotenv import load_dotenv

from app import seek_confirmation
from app.decorators.datetime_decorators import dt_to_date
from app.decorators.number_decorators import fmt_n
from app.bq_base_grapher import BigQueryBaseGrapher

load_dotenv()

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
        print("SELECTED WEEK:")
        #row = random.choice(self.rows) # TODO: see which ones have not already been graphed, and take the first one
        wk = self.weeks[1] # TODO: see which ones have not already been graphed, and take the first one
        wk_id = f"{wk.year}-{str(wk.week).zfill(2)}"
        print(wk_id)
        pprint(dict(wk))

        seek_confirmation()

        breakpoint()
        #self.storage_service = GraphStorageService(
        #    local_dirpath = os.path.join(DATA_DIR, "graphs", "weekly", wk_id),
        #    gcs_dirpath = os.path.join("storage", "data", "graphs", "weekly", wk_id)
        #)

        self.tweets_start_at = tweets_start_at
        self.tweets_end_at = tweets_start_at

        self.write_metadata_to_file()
        self.upload_metadata()

        self.start()
        self.graph = DiGraph()
        self.running_results = []

        for row in self.bq.fetch_retweet_counts_in_batches(start_at=self.tweets_start_at, end_at=self.tweets_end_at):


            breakpoint()




if __name__ == "__main__":

    grapher = BigQueryWeeklyRetweetGrapher()

    grapher.perform()
