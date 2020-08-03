
import os
from pprint import pprint
from dotenv import load_dotenv

from app import seek_confirmation
from app.decorators.datetime_decorators import dt_to_date
from app.decorators.number_decorators import fmt_n
from app.bq_base_grapher import BigQueryBaseGrapher

load_dotenv()

TWEETS_START_AT = os.getenv("TWEETS_START_AT", default="2019-12-15 00:00:00")
TWEETS_END_AT = os.getenv("TWEETS_START_AT", default="2020-03-21 23:59:59")

class BigQueryWeeklyRetweetGrapher(BigQueryBaseGrapher):

    def __init__(self, tweets_start_at=TWEETS_START_AT, tweets_end_at=TWEETS_END_AT):
        super().__init__()
        self.tweets_start_at = tweets_start_at
        self.tweets_end_at = tweets_end_at

    def perform(self):
        print("--------------------")
        print("FETCHING WEEKS...")
        self.rows = list(self.bq_service.fetch_retweet_weeks())

        print("--------------------")
        print("WEEKS:")
        for row in self.rows:
            print("   ",
                f"{row.year}-{str(row.week).zfill(2)}",
                f"('{dt_to_date(row.min_created)}' - '{dt_to_date(row.max_created)}')", "|",
                f"DAYS: {fmt_n(row.day_count)}", "|",
                f"USERS: {fmt_n(row.user_count)}", "|",
                f"RETWEETS: {fmt_n(row.retweet_count)}"
             )
            #pprint(dict(row))
            #breakpoint()

        seek_confirmation()
        breakpoint()


if __name__ == "__main__":

    grapher = BigQueryWeeklyRetweetGrapher()

    grapher.perform()
