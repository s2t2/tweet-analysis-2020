
import os
from datetime import datetime, timedelta
from pprint import pprint
import time

from dotenv import load_dotenv
from pandas import date_range

from app import seek_confirmation
from app.decorators.datetime_decorators import dt_to_s, dt_to_date
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.retweet_grapher import RetweetGrapher

load_dotenv()

START_DATE = os.getenv("START_DATE", default="2020-01-01") # the first period will start on this day
K_DAYS = int(os.getenv("K_DAYS", default="3")) # the length of each time period in days
N_PERIODS = int(os.getenv("N_PERIODS", default="5")) # the number of periods to construct

def get_date_ranges(start_date="2020-01-01", k_days=3, n_periods=5):
    """
    Params:
        start_date (str) date string like "2020-01-01"
        k_days (int) number of days in each period
        n_periods (int) number of periods
    """
    date_ranges = []
    period_start_at = datetime.strptime(start_date, "%Y-%m-%d")
    for i in range(0, n_periods):
        period_end_at = period_start_at + timedelta(days=k_days) - timedelta(seconds=1)
        date_ranges.append(DateRange(period_start_at, period_end_at))
        period_start_at = period_end_at + timedelta(seconds=1)
    return date_ranges

class DateRange:
    def __init__(self, start_at, end_at):
        self.start_at = start_at
        self.end_at = end_at

    def __repr__(self):
        return f"<DateRange start_date={self.start_date} end_date={self.end_date} >"

    @property
    def start_date(self):
        return dt_to_date(self.start_at)

    @property
    def end_date(self):
        return dt_to_date(self.end_at)


if __name__ == "__main__":

    bq_service = BigQueryService()

    print("-------------------------")
    print("DATE RANGES...")
    date_ranges = get_date_ranges(start_date=START_DATE, k_days=K_DAYS, n_periods=N_PERIODS)
    pprint(date_ranges)
    seek_confirmation()

    for date_range in date_ranges:
        print("\n \n")

        dirpath = f"retweet_graphs_v2/{K_DAYS}_days/{START_DATE}/{date_range.start_date}"
        graph_storage = GraphStorage(dirpath=dirpath)

        grapher = RetweetGrapher(
            graph_storage=graph_storage,
            bq_service=bq_service,
            tweets_start_at=date_range.start_at,
            tweets_end_at=date_range.end_at,
        )
        #pprint(grapher.metadata)
        #grapher.save_metadata()
        #grapher.start()
        #grapher.perform()
        #grapher.end()
        #grapher.report()
        #grapher.save_results()
        #grapher.save_graph()
        #grapher.sleep() # maybe mini nap for 3 minutes to cool memory?

        del grapher # clear memory!

    print("JOB COMPLETE!")
    time.sleep(6 * 60 * 60) # 6 hours, enough time to stop the server before it restarts
