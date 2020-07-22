
import os
from datetime import datetime
from pprint import pprint

import numpy as np
from scipy.stats import kstest, ks_2samp
from dotenv import load_dotenv

from app.models import db, BoundSession, RetweeterDetail
from app.workers import to_dt, to_ts, fmt_n

load_dotenv()
np.random.seed(2020)

X_COL = os.getenv("X_COL", default="maga") # an attribute name of UserDetail
Y_COL = os.getenv("Y_COL", default="impeach_and_remove") # an attribute name of UserDetail

class Analyzer:

    def __init__(self, pg=None, x_col=X_COL, y_col=Y_COL):
        self.cursor = pg or db # consider using a row factory for dictionary-like results
        self.x_col = x_col
        self.y_col = y_col
        print("--------------------------------------")
        print("RETWEETER CREATION DATE ANALYZER...")
        print(f"TWO TOPICS: '{x_col.upper()}' | '{y_col.upper()}'")

    def comparison_counts(self):
        sql = f"""
            SELECT
                 count(distinct CASE WHEN d.{self.x_col} > 0 and d.{self.y_col} > 0 THEN user_id END) both_count
                ,count(distinct CASE WHEN d.{self.x_col} = 0 and d.{self.y_col} = 0 THEN user_id END) neither_count
                ,count(distinct CASE WHEN d.{self.x_col} > 0 and d.{self.y_col} = 0 THEN user_id END) x_count
                ,count(distinct CASE WHEN d.{self.x_col} = 0 AND d.{self.y_col} > 0 THEN user_id END) y_count
            FROM retweeter_details d
        """
        return self.cursor.execute(sql)

if __name__ == "__main__":


    analyzer = Analyzer()

    results = analyzer.comparison_counts().fetchone()
    print("BOTH:", fmt_n(results[0]))
    print("NEITHER:", fmt_n(results[1]))
    print(f"X ({analyzer.x_col.upper()}):", fmt_n(results[2]))
    print(f"Y ({analyzer.y_col.upper()}):", fmt_n(results[3]))



    #breakpoint()
