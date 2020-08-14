
import os
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

from app import seek_confirmation
from app.decorators.datetime_decorators import dt_to_date

load_dotenv()

START_DATE = os.getenv("START_DATE", default="2020-01-01") # the first period will start on this day
K_DAYS = int(os.getenv("K_DAYS", default="3")) # the length of each time period in days
N_PERIODS = int(os.getenv("N_PERIODS", default="5")) # the number of periods to construct

class DateRangeGenerator:
    def __init__(self, start_date=START_DATE, k_days=K_DAYS, n_periods=N_PERIODS):
        """
        Generates a list of date ranges.

        Params:
            start_date (str) the first period start date, like "2020-01-01"
            k_days (int) number of days in each period
            n_periods (int) number of periods
        """
        self.start_date = start_date
        self.k_days = int(k_days)
        self.n_periods = int(n_periods)

        print("-------------------------")
        print("DATE RANGE GENERATOR...")
        print("  START DATE:", self.start_date)
        print("  K DAYS:", self.k_days)
        print("  N PERIODS:", self.n_periods)

        print("-------------------------")
        print("DATE RANGES...")
        self.date_ranges = self.get_date_ranges(start_date=self.start_date, k_days=self.k_days, n_periods=self.n_periods)
        pprint(self.date_ranges)
        seek_confirmation()

    @staticmethod
    def get_date_ranges(start_date, k_days, n_periods):
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
        """Params: start_at, end_at (datetime) like datetime(2020, 1, 31) """
        self.start_at = start_at
        self.end_at = end_at

    def __repr__(self):
        return f"<DateRange start_at='{self.start_at}' end_at={self.end_at}>"

    @property
    def metadata(self):
        return {"start_date": self.start_date, "end_date": self.end_date}

    @property
    def start_date(self):
        return dt_to_date(self.start_at)

    @property
    def end_date(self):
        return dt_to_date(self.end_at)


if __name__ == "__main__":

    gen = DateRangeGenerator()
