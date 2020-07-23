


import os
from dotenv import load_dotenv

load_dotenv()

TOPIC = os.getenv("TOPIC", default="#MAGA")
PVAL_MAX = float(os.getenv("PVAL_MAX", default="0.01")) # the maximum pvalue under which to reject the ks test null hypothesis

def to_ts(dt):
    """
    Converts datetime object to timestamp (seconds since epoch). Should be inverse of to_dt().

    Param: dt (datetime) like ... datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)

    Returns: (float) like ... 1469270315.6363637
    """
    return int(dt.timestamp())

def to_dt(ts):
    """
    Converts timestamp (seconds since epoch) to datetime object. Should be inverse of to_ts().

    Param: ts (float) seconds since epoch like ... 1469270315.6363637

    Returns: (datetime) like ... datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)
    """
    return datetime.utcfromtimestamp(ts)

def fmt_date(ts):
    """
    Converts timestamp (seconds since epoch) to date string object.

    Param: ts (float) seconds since epoch like ... 1469270315.6363637

    Returns: (str) like ... "2014-02-10"
    """
    return to_dt(ts).strftime("%Y-%m-%d")

def interpret_ks(result, pval_max=0.01):
    """
    Interprets the results of a KS test, indicates whether or not to reject the null hypothesis.
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
    Performs two-sample KS test on two independent populations of users: those retweeting about a topic vs those not.
    Fetching strategy fetch_xy() can be customized in child classes.
    """

    def __init__(self, bq=None, topic=TOPIC, pval_max=PVAL_MAX):
        self.bq = bq or BigQueryService()
        self.topic = topic
        self.pval_max = pval_max

        self.x = []
        self.y = []

    #def fetch_xy(self):
    #    """
    #    To be implemented in child class: populate self.x and self.y with two independent samples from a continuous distribution.
    #    For example, fetch the created at date for each user and use the to_ts() function to convert it into seconds since epoch.
    #    """
    #    raise NotImplementedError

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
    @lru_cache(maxsize=None)
    def report(self):
        self.xy_result # make sure data is fetched and test has been performed before reporting out
        return {
            "row_id": self.row_id,
            "topic": self.topic,
            "pval_max": self.pval_max,
            "x_size": self.x_size, "x_avg_date": self.x_avg_date, "x_avg": self.x_avg,
            "y_size": self.y_size, "y_avg_date": self.y_avg_date, "y_avg": self.y_avg,
            "ks_stat": self.xy_result.statistic,
            "ks_pval": self.xy_result.pvalue,
            "ks_inter": interpret_ks(self.xy_result, self.pval_max)
        }

    @property
    def row_id(self):
        """should be unique for each set of results"""
        return self.topic.lower().replace(" ","") #> "#sometag"

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

    def append_results_to_csv(self, csv_filepath):
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
