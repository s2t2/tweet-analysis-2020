
import os
from functools import lru_cache
from pprint import pprint

from dotenv import load_dotenv
import numpy as np
from scipy.stats import ks_2samp
from pandas import DataFrame, read_csv, concat

from app import DATA_DIR
from app.datetime_helpers import to_ts, fmt_date
from app.bq_service import BigQueryService
from app.ks_test.interpreter import interpret, PVAL_MAX

load_dotenv()

TOPIC = os.getenv("TOPIC", default="#MAGA")
RESULTS_CSV_FILEPATH = os.path.join(DATA_DIR, "ks_retweeter_ages_by_topic.csv")

class TopicAnalyzer:
    """
    Performs two-sample KS test on two independent populations of users: those retweeting about a topic vs those not.
    Fetching strategy fetch_xy() can be customized in child classes to compare different independent user populations.
    """

    def __init__(self, bq=None, topic=TOPIC, pval_max=PVAL_MAX, results_csv_filepath=RESULTS_CSV_FILEPATH):
        self.topic = topic

        self.bq = bq or BigQueryService()
        self.x = []
        self.y = []

        self.pval_max = pval_max
        self.interpret_ks = interpret
        self.results_csv_filepath = results_csv_filepath

    def fetch_xy(self):
        print("FETCHING RETWEETERS...")
        for row in self.bq.fetch_retweeters_by_topic_exclusive(self.topic):
            ts = to_ts(row.user_created_at)
            if row.count > 0:
                self.x.append(ts)
            else:
                self.y.append(ts)

    @property
    @lru_cache(maxsize=None)
    def xy_result(self):
        if not self.x and not self.y: self.fetch_xy() # make sure data is fetched before trying to test it
        print("-----------------------------")
        print("TWO-SAMPLE KS TEST...")
        result = ks_2samp(self.x, self.y)
        print(type(result))
        return result #> <class 'scipy.stats.stats.KstestResult'>

    @property
    def x_size(self):
        return len(self.x) #> int

    @property
    def y_size(self):
        return len(self.y) #> int

    @property
    def x_avg(self):
        return np.mean(self.x) #> float (seconds since epoch)

    @property
    def y_avg(self):
        return np.mean(self.y) #> float (seconds since epoch)

    @property
    def x_avg_date(self):
        return fmt_date(self.x_avg) #> date string

    @property
    def y_avg_date(self):
        return fmt_date(self.y_avg) #> date string

    @property
    @lru_cache(maxsize=None)
    def report(self):
        self.xy_result # make sure data is fetched and test has been performed before reporting out
        return {
            "row_id": self.row_id,
            "topic": self.topic,
            "x_size": self.x_size,
            "y_size": self.y_size,
            "x_avg": self.x_avg,
            "y_avg": self.y_avg,
            "x_avg_date": self.x_avg_date,
            "y_avg_date": self.y_avg_date,
            "ks_stat": self.xy_result.statistic,
            "ks_pval": self.xy_result.pvalue,
            "pval_max": self.pval_max,
            "ks_inter": self.interpret_ks(self.xy_result, self.pval_max)
        }

    @property
    def row_id(self):
        """should be unique for each topic in the CSV file"""
        return self.topic.lower().replace(" ","") #> "#maga"

    def append_results_to_csv(self, csv_filepath=None):
        csv_filepath = csv_filepath or self.results_csv_filepath
        print("WRITING TO FILE...", csv_filepath)
        df = DataFrame(self.report, index=["row_id"])

        if os.path.isfile(csv_filepath):
            existing_df = read_csv(csv_filepath)
            new_df = concat([existing_df, df])
            new_df.drop_duplicates(subset=["row_id"], inplace=True, keep="first")
            new_df.to_csv(csv_filepath, index=False)
            return new_df
        else:
            df.to_csv(csv_filepath, index=False)
            return df


if __name__ == "__main__":

    analyzer = TopicAnalyzer()
    pprint(analyzer.report)
    analyzer.append_results_to_csv()
