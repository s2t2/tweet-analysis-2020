
import os
from pprint import pprint
from dotenv import load_dotenv

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
        self.weeks = list(self.grapher.bq_service.fetch_weeks())

        week = self.weeks[0]
        pprint(dict(week))
        breakpoint()




if __name__ == "__main__":

    grapher = BigQueryWeeklyRetweetGrapher()

    grapher.perform()
