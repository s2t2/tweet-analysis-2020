
import os
from pprint import pprint
import json
from functools import lru_cache


from dotenv import load_dotenv
import numpy as np
from pandas import DataFrame, read_csv, concat
from scipy.stats import kstest, ks_2samp

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.workers import to_dt, to_ts, fmt_n

load_dotenv()
np.random.seed(2020)

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")
PVAL_MAX = float(os.getenv("PVAL_MAX", default="0.01")) # the maximum pvalue under which to reject the ks test null hypothesis

RESULTS_CSV_FILEPATH = os.path.join(DATA_DIR, "retweeter_ks2_test_results.csv")

def ts_to_date(my_ts):
    return to_dt(my_ts).strftime("%Y-%m-%d")

def interpret_ks(result, pval_max=0.01):
    """
    Interprets the results of a two-sample KS test, indicates whether or not to reject the null hypothesis.
    "Under the null hypothesis, the two distributions are identical."
    "If the KS statistic is small or the p-value is high, then we cannot reject the null hypothesis."

    See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html

    Params:
        result (scipy.stats.stats.KstestResult)
        pval_max (float) the maximum pvalue threshold under which to reject the null hypothesis

    """
    interpretation = "ACCEPT (SAME)"
    if result.pvalue <= pval_max:
        interpretation = "REJECT (DIFF)"
    return interpretation

class Analyzer:
    """
    Performs two-sample KS test on two independent populations of users talking about two different topics.
    """

    def __init__(self, bq=None, x_topic=X_TOPIC, y_topic=Y_TOPIC, pval_max=PVAL_MAX, results_csv_filepath=RESULTS_CSV_FILEPATH):
        self.bq = bq or BigQueryService.cautiously_initialized()
        self.x_topic = x_topic
        self.y_topic = y_topic
        self.pval_max = pval_max
        self.results_csv_filepath = results_csv_filepath

        self.x = []
        self.y = []

    def fetch_xy(self):
        #print("-----------------------------")
        print("FETCHING RETWEETERS...")
        for row in self.bq.fetch_retweeters_by_topic_exclusive(self.x_topic, self.y_topic):
            ts = to_ts(row.user_created_at)
            if row.x_count > 0 and row.y_count == 0:
                self.x.append(ts)
            elif row.x_count == 0 and row.y_count > 0:
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
    @lru_cache(maxsize=None)
    def report(self):
        self.xy_result # make sure data is fetched and test has been performed before reporting out
        return {
            "topics_id": self.topics_id,
            "x_topic": self.x_topic,
            "y_topic": self.y_topic,
            "pval_max": self.pval_max,
            "x_size": self.x_size, "x_avg_date": self.x_avg_date, "x_avg": self.x_avg,
            "y_size": self.y_size, "y_avg_date": self.y_avg_date, "y_avg": self.y_avg,
            "ks_stat": self.xy_result.statistic,
            "ks_pval": self.xy_result.pvalue,
            "ks_inter": interpret_ks(self.xy_result, self.pval_max)
        }

    @property
    def topics_id(self):
        """should be unique for each pair of topics, and able to be used in file names"""
        sorted_topics = sorted([self.x_topic.lower().replace(" ",""), self.y_topic.lower().replace(" ","")])
        return "_".join(sorted_topics) #> "#sometag_#othertag"

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
        return ts_to_date(self.x_avg) #> date string

    @property
    def y_avg_date(self):
        return ts_to_date(self.y_avg) #> date string

    def append_results_to_csv(self, csv_filepath=None):
        csv_filepath = csv_filepath or self.results_csv_filepath
        print("WRITING TO FILE...", csv_filepath)
        df = DataFrame(self.report, index=["topics_id"])

        if os.path.isfile(csv_filepath):
            existing_df = read_csv(csv_filepath)
            new_df = concat([existing_df, df])
            new_df.drop_duplicates(subset=["topics_id"], inplace=True, keep="first")
            new_df.to_csv(csv_filepath, index=False)
            return new_df
        else:
            df.to_csv(csv_filepath, index=False)
            return df

if __name__ == "__main__":

    analyzer = Analyzer()
    pprint(analyzer.report)
    analyzer.append_results_to_csv()
