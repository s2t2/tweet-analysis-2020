
import os
from dotenv import load_dotenv

from app.decorators.datetime_decorators import dt_to_s, dt_to_date
from app.bq_service import BigQueryService

EVENT_NAME = os.getenv("EVENT_NAME", default="impeachment") # name of local dir where graphs will be stored
START_DATE = os.getenv("START_DATE", default="2020-01-01") # the first period will start on this day
K_DAYS = int(os.getenv("K_DAYS", default="3")) # the length of each time period in days
N_PERIODS = int(os.getenv("N_PERIODS", default="15")) # the number of periods to construct

class TimePeriod:
    def __init__(self, row):
        self.row = row

    @property
    def id(self):
        return dt_to_date(self.start_at)

    @property
    def start_at(self):
        return self.row.tweets_start_at

    @property
    def end_at(self):
        return self.row.tweets_end_at

if __name__ == "__main__":

    bq_service = BigQueryService()

    time_periods = [TimePeriod(row) for row in bq_service.fetch_daily_retweet_periods(k_days=K_DAYS, n_periods=N_PERIODS)]
    breakpoint()

    for time_period in time_periods:
        print(time_period.start_at, time_period.end_at)
        dirpath = f"data/retweet_graphs_v2/{EVENT_NAME}/k_days/{period.id}/K{K_DAYS}_N{N_PERIODS}"
        print(dirpath)

        #graph_storage = GraphStorage(dirpath=dirpath)
        #grapher = RetweetGrapher(
        #    bq_service=bq_service,
        #    graph_storage=graph_storage,
        #    tweets_start_at=dt_to_s(time_period.start_at),
        #    tweets_end_at=dt_to_s(time_period.end_at),
        #)
        #grapher.perform()
        #grapher.sleep()
