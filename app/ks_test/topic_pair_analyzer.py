
import os
from pprint import pprint
from functools import lru_cache

from dotenv import load_dotenv

from app import DATA_DIR
from app.datetime_helpers import to_ts
from app.ks_test.topic_analyzer import TopicAnalyzer

load_dotenv()

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")

RESULTS_CSV_FILEPATH = os.path.join(DATA_DIR, "ks_retweeter_ages_by_topic_pair.csv")

class TopicPairAnalyzer(TopicAnalyzer):
    """
    Performs two-sample KS test on two independent populations of users talking about two different topics.
    One sample is for users talking about topic x and not y.
    The other sample is for users talking about topic y and not x.
    """

    def __init__(self, x_topic=X_TOPIC, y_topic=Y_TOPIC, results_csv_filepath=RESULTS_CSV_FILEPATH):
        super().__init__(results_csv_filepath=RESULTS_CSV_FILEPATH, topic=None) # topic None feels hacky, but its ok, we'll remove it from reporting
        self.x_topic = x_topic
        self.y_topic = y_topic

    def fetch_xy(self):
        print("FETCHING RETWEETERS...")
        for row in self.bq.fetch_retweeters_by_topics_exclusive(self.x_topic, self.y_topic):
            ts = to_ts(row.user_created_at)
            if row.x_count > 0 and row.y_count == 0:
                self.x.append(ts)
            elif row.x_count == 0 and row.y_count > 0:
                self.y.append(ts)

    @property
    @lru_cache(maxsize=None)
    def report(self):
        self.xy_result # make sure data is fetched and test has been performed before reporting out
        return {
            "row_id": self.row_id,
            "x_topic": self.x_topic,
            "y_topic": self.y_topic,
            "x_size": self.x_size,
            "x_avg_date": self.x_avg_date,
            "x_avg": self.x_avg,
            "y_size": self.y_size,
            "y_avg_date": self.y_avg_date,
            "y_avg": self.y_avg,
            "ks_stat": self.xy_result.statistic,
            "pval_max": self.pval_max,
            "ks_pval": self.xy_result.pvalue,
            "ks_inter": self.interpret_ks(self.xy_result, self.pval_max)
        }

    @property
    def row_id(self):
        """should be unique for each pair of topics in the CSV file"""
        sorted_topics = sorted([self.x_topic.lower().replace(" ",""), self.y_topic.lower().replace(" ","")])
        return "_".join(sorted_topics) #> "#sometag_#othertag"

if __name__ == "__main__":

    analyzer = TopicPairAnalyzer()
    pprint(analyzer.report)
    analyzer.append_results_to_csv()
