
import os
from pprint import pprint

import numpy as np
from scipy.stats import kstest, ks_2samp
from dotenv import load_dotenv

from app.bq_service import BigQueryService
from app.workers import to_dt, to_ts, fmt_n

load_dotenv()
np.random.seed(2020)

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")


def to_date(my_ts):
    return to_dt(my_ts).strftime("%Y-%m-%d")

if __name__ == "__main__":

    x_topic = X_TOPIC.upper()
    y_topic = Y_TOPIC.upper()

    bq = BigQueryService.cautiously_initialized()

    # get the users talking about topic x and not y
    # for each user, determine how many times they were talking about topic x and y
    # then label the user x, y, neither, or both

    sql = f"""

        SELECT
            rt.user_id
            ,rt.user_created_at
            ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '{x_topic}') then rt.status_id end) as x_count
            ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '{y_topic}') then rt.status_id end) as y_count
        FROM {bq.dataset_address}.retweets rt
        -- WHERE REGEXP_CONTAINS(upper(rt.status_text), '{x_topic}') OR REGEXP_CONTAINS(upper(rt.status_text), '{y_topic}')
        GROUP BY 1,2
        -- HAVING (x_count > 0 and y_count = 0) OR (x_count = 0 and y_count > 0)

    """
    print(sql)

    x, y = [], []
    both, neither = [], []

    print("-----------------------------")
    print("FETCHING USERS...")
    for row in bq.execute_query(sql):
        ts = to_ts(row.user_created_at)

        if row.x_count == 0 and row.y_count == 0:
            neither.append(ts)
        elif row.x_count > 0 and row.y_count == 0:
            x.append(ts)
        elif row.x_count == 0 and row.y_count > 0:
            y.append(ts)
        elif row.x_count > 0 and row.y_count > 0:
            both.append(ts)

    print("X:", fmt_n(len(x)))
    print("Y:", fmt_n(len(y)))
    print("BOTH:", fmt_n(len(both)))
    print("NEITHER:", fmt_n(len(neither)))

    print("-----------------------------")
    print("COMPARING CREATION DATES...")
    x_avg, y_avg = np.mean(x), np.mean(y)
    both_avg, neither_avg = np.mean(both), np.mean(neither)

    print("X:", to_date(x_avg))
    print("Y:", to_date(y_avg))
    print("BOTH:", to_date(both_avg))
    print("NEITHER:", to_date(neither_avg))

    print("TWO-SAMPLE KS TEST...")
    xy_result = ks_2samp(x, y)
    xn_result = ks_2samp(x, neither)
    yn_result = ks_2samp(y, neither)
    xb_result = ks_2samp(x, both)
    yb_result = ks_2samp(y, both)

    # Under the null hypothesis, the two distributions are identical
    # If the KS statistic is small or the p-value is high, then we cannot reject the hypothesis that the distributions of the two samples are the same.

    comparison_id = f"{x_topic.replace(' ', '').lower()}_vs_{y_topic.replace(' ', '').lower()}"
    results = {
        "id": comparison_id,
        "topics": {"x": X_TOPIC, "y": Y_TOPIC},
        "samples": {
            "x": {"size": len(x), "avg": int(x_avg), "avg_date": to_date(x_avg)},
            "y": {"size": len(y), "avg": int(y_avg), "avg_date": to_date(y_avg)},
            "both": {"size": len(x), "avg": int(both_avg), "avg_date": to_date(both_avg)},
            "neither": {"size": len(x), "avg": int(neither_avg), "avg_date": to_date(neither_avg)},
        },
        "results": {
            "x vs y":       {"stat": xy_result.statistic, "pval": xy_result.pvalue}, # "interpretation":"REJECT"
            "x vs neither": {"stat": xn_result.statistic, "pval": xn_result.pvalue}, # "interpretation":"REJECT"
            "y vs neither": {"stat": yn_result.statistic, "pval": yn_result.pvalue}, # "interpretation":"REJECT"
            "x vs both":    {"stat": xb_result.statistic, "pval": xb_result.pvalue}, # "interpretation":"REJECT"
            "y vs both":    {"stat": yb_result.statistic, "pval": yb_result.pvalue}, # "interpretation":"REJECT"
        }
    }
    pprint(results)

    breakpoint()
