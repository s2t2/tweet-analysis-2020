
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pandas import date_range

from app.decorators.datetime_decorators import dt_to_s, dt_to_date
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage

load_dotenv()

#EVENT_NAME = os.getenv("EVENT_NAME", default="impeachment") # name of local dir where graphs will be stored

START_DATE = os.getenv("START_DATE", default="2020-01-01") # the first period will start on this day
K_DAYS = int(os.getenv("K_DAYS", default="3")) # the length of each time period in days
N_PERIODS = int(os.getenv("N_PERIODS", default="5")) # the number of periods to construct

def get_date_ranges(start_date=START_DATE, k_days=K_DAYS, n_periods=N_PERIODS):
    """
    Params:
        start_date (str) date string like "2020-01-01"
        k_days (int) number of days in each period
        n_periods (int) number of periods
    """
    date_ranges = []
    period_start = datetime.strptime(start_date, "%Y-%m-%d")
    for i in range(0, n_periods):
        period_end = period_start + timedelta(days=k_days) - timedelta(seconds=1)
        date_ranges.append({"start_date": period_start, "end_date": period_end})
        period_start = period_end + timedelta(seconds=1)
    return date_ranges



if __name__ == "__main__":

    #bq_service = BigQueryService()

    for date_range in get_date_ranges(start_date=START_DATE, k_days=K_DAYS, n_periods=N_PERIODS):
        #dirpath = f"data/retweet_graphs_v2/{EVENT_NAME}/k_days/{K_DAYS}/{dt_to_date(date_range['start_date'])}/"
        #dirpath = f"data/{EVENT_NAME}/retweet_graphs_v2/k_days/{K_DAYS}/{dt_to_date(date_range['start_date'])}/"
        dirpath = f"retweet_graphs_v2/{K_DAYS}_days/{dt_to_date(date_range['start_date'])}/"
        #print(dirpath)

        graph_storage = GraphStorage(dirpath=dirpath)

        #grapher = RetweetGrapher(
        #    bq_service=bq_service,
        #    graph_storage=graph_storage,
        #    tweets_start_at=dt_to_s(time_period.start_at),
        #    tweets_end_at=dt_to_s(time_period.end_at),
        #)
        #grapher.perform()
        #grapher.sleep()
