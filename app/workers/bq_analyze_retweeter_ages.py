
import os
from pprint import pprint
import json
from functools import lru_cache

import numpy as np
from scipy.stats import kstest, ks_2samp
from dotenv import load_dotenv

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.workers import to_dt, to_ts, fmt_n

load_dotenv()
np.random.seed(2020)

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")
PVAL_MAX = float(os.getenv("PVAL_MAX", default="0.01"))

# KS_RESULTS_DIR = os.path.join(DATA_DIR, "ks_tests")

def ts_to_date(my_ts):
    return to_dt(my_ts).strftime("%Y-%m-%d")

def interpret_ks(self, ks_test_results, pval_max):
    """
    A utility function to interpret the results of a two-sample KS test.
    Indicates whether or not to reject the null hypothesis.

    See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html

    Methodology Notes / Docs:
        Under the null hypothesis, the two distributions are identical.
        If the KS statistic is small or the p-value is high, then we cannot reject the null hypothesis.

    """
    if ks_test_results.pvalue <= pval_max:
        interpretation = "REJECT (DIFF)"
    else:
        interpretation = "ACCEPT (SAME)"
    return interpretation

class Analyzer:
    """
    Performs two-sample KS test on two independent populations of users talking about two different topics.
    """

    def __init__(self, bq=None, x_topic=X_TOPIC, y_topic=Y_TOPIC, pval_max=PVAL_MAX):
        self.bq = bq or BigQueryService.cautiously_initialized()

        self.x_topic = x_topic
        self.y_topic = y_topic
        self.pval_max = pval_max

        self.x, self.y = [], []

    @property
    def x_size(self):
        return len(self.x)

    @property
    def y_size(self):
        return len(self.y)

    @property
    def x_avg(self):
        return np.mean(self.x)

    @property
    def y_avg(self):
        return np.mean(self.y)

    @property
    def x_avg_date(self):
        return ts_to_date(self.x_avg)

    @property
    def y_avg_date(self):
        return ts_to_date(self.y_avg)

    @property
    @lru_cache(maxsize=None)
    def xy_result(self):
        return ks_2samp(self.x, self.y)

    @property
    def topics_filename(self):
        """should be unique for each pair of topics, and able to be used in file names"""
        sorted_topics = sorted([self.x_topic.lower().replace(" ",""), self.y_topic.lower().replace(" ","")])
        return "_".join(sorted_topics)


    def perform(self):
        print("-----------------------------")
        print("FETCHING RETWEETERS...")
        for row in self.bq.fetch_retweeters_by_topic_exclusive(self.x_topic, self.y_topic):
            ts = to_ts(row.user_created_at)
            if row.x_count > 0 and row.y_count == 0:
                self.x.append(ts)
            elif row.x_count == 0 and row.y_count > 0:
                self.y.append(ts)
        print("X SIZE:", fmt_n(self.x_size))
        print("Y SIZE:", fmt_n(self.y_size))
        print("X AVG:", self.x_avg_date)
        print("Y AVG:", self.y_avg_date)

        print("-----------------------------")
        print("TWO-SAMPLE KS TESTS...")

        response = {
            "id": self.topics_filename,
            "settings": {"x_topic": self.x_topic, "y_topic": self.y_topic, "pval_max": self.pval_max}
            "samples": {
                "x": {"size": self.x_size, "avg_date": self.x_avg_date, "avg_age": self.x_avg},
                "y": {"size": self.y_size, "avg_date": self.y_avg_date, "avg_age": self.y_avg},
            },
            "results": {
                "stat": self.xy_result.statistic,
                "pval": self.xy_result.pvalue
                "interpretation": interpret(self.xy_result, self.pval_max)
            }
        }
        return response

if __name__ == "__main__":

    analyzer = Analyzer()

    resp = analyzer.perform()
    pprint(resp)

    print("WRITING TO FILE...")
    # TODO: pandas append to CSV
