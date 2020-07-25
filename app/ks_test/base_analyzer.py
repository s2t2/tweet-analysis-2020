
#import os
#from functools import lru_cache
#
#from dotenv import load_dotenv
#import numpy as np
#from scipy.stats import ks_2samp
#from pandas import DataFrame, read_csv, concat
#
#from app import DATA_DIR
#from app.bq_service import BigQueryService
#from app.ks_test.interpreter import interpret, PVAL_MAX
#
#load_dotenv()
#
#class BaseAnalyzer:
#    """
#    An abstract class for performing two-sample KS test on two independent populations of users from BigQuery.
#    The fetching strategy fetch_xy() can be customized in child classes to compare different independent user populations.
#    """
#
#    def __init__(self, bq=None, pval_max=PVAL_MAX):
#        self.pval_max = pval_max
#        self.bq = bq or BigQueryService()
#        self.x = []
#        self.y = []
#
#    def fetch_xy(self):
        """
        Should populate contents of self.x and self.y, each representing a sample of a continuous numeric variable
        (e.g. user creation dates as seconds since epoch).
        """
        raise NotImplementedError
#
#    @property
#    @lru_cache(maxsize=None)
#    def xy_result(self):
#        if not self.x and not self.y: self.fetch_xy() # make sure data is fetched before trying to test it
#        print("-----------------------------")
#        print("TWO-SAMPLE KS TEST...")
#        result = ks_2samp(self.x, self.y)
#        print(type(result))
#        return result #> <class 'scipy.stats.stats.KstestResult'>
#
#    @property
#    @lru_cache(maxsize=None)
#    def report(self):
#        self.xy_result # make sure data is fetched and test has been performed before reporting out
#        return {
#            "row_id": self.row_id,
#            #"topic": self.topic,
#            "x_size": self.x_size,
#            "y_size": self.y_size,
#            "x_avg": self.x_avg,
#            "y_avg": self.y_avg,
#            "x_avg_date": self.x_avg_date,
#            "y_avg_date": self.y_avg_date,
#            "ks_stat": self.xy_result.statistic,
#            "ks_pval": self.xy_result.pvalue,
#            "pval_max": self.pval_max,
#            "ks_inter": interpret_ks(self.xy_result, self.pval_max)
#        }
#
#    @property
#    def row_id(self):
#        """
#        If the results of this test are inserted as a row in a CSV file, this should uniquely identify the row.
#        """
#        #return self.topic.lower().replace(" ","")
#        raise NotImplementedError
#
#    @property
#    def x_size(self):
#        return len(self.x) #> int
#
#    @property
#    def y_size(self):
#        return len(self.y) #> int
#
#    @property
#    def x_avg(self):
#        return np.mean(self.x) #> float (seconds since epoch)
#
#    @property
#    def y_avg(self):
#        return np.mean(self.y) #> float (seconds since epoch)
#
#    @property
#    def x_avg_date(self):
#        return fmt_date(self.x_avg) #> date string
#
#    @property
#    def y_avg_date(self):
#        return fmt_date(self.y_avg) #> date string
#
#    def append_results_to_csv(self, csv_filepath):
#        print("WRITING TO FILE...", csv_filepath)
#        df = DataFrame(self.report, index=["row_id"])
#
#        if os.path.isfile(csv_filepath):
#            existing_df = read_csv(csv_filepath)
#            new_df = concat([existing_df, df])
#            new_df.drop_duplicates(subset=["row_id"], inplace=True, keep="first")
#            new_df.to_csv(csv_filepath, index=False)
#            return new_df
#        else:
#            df.to_csv(csv_filepath, index=False)
#            return df
#
