
import os
from pprint import pprint
import json

import numpy as np
from scipy.stats import kstest, ks_2samp
from dotenv import load_dotenv

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.workers import fmt_n
from app.ks_test_helper import to_dt, to_ts

load_dotenv()
np.random.seed(2020)

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")

KS_RESULTS_DIR = os.path.join(DATA_DIR, "ks_tests")

def to_date(my_ts):
    return to_dt(my_ts).strftime("%Y-%m-%d")

def interpret(ks_test_results, pval_max=0.01):
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



if __name__ == "__main__":

    x_topic = X_TOPIC.upper()
    y_topic = Y_TOPIC.upper()
    comparison_id = f"{x_topic.replace(' ', '').lower()}_{y_topic.replace(' ', '').lower()}"

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

    # If the mode is "auto", the computation is exact if the sample sizes are less than 10,000.
    # ... For larger sizes, the computation uses the KS distributions to compute an approximate value.
    #
    # The ‘two-sided’ ‘exact’ computation computes the complementary probability and then subtracts from 1.
    # ... As such, the minimum probability it can return is about 1e-16.
    # ... While the algorithm itself is exact, numerical errors may accumulate for large sample sizes. It is most suited to situations in which one of the sample sizes is only a few thousand.

    print("-----------------------------")
    print("COMPARING CREATION DATES...")
    x_avg, y_avg = np.mean(x), np.mean(y)
    both_avg, neither_avg = np.mean(both), np.mean(neither)

    print("X:", to_date(x_avg))
    print("Y:", to_date(y_avg))
    print("BOTH:", to_date(both_avg))
    print("NEITHER:", to_date(neither_avg))

    print("-----------------------------")
    print("TWO-SAMPLE KS TESTS...")

    xy_result = ks_2samp(x, y)
    xn_result = ks_2samp(x, neither)
    yn_result = ks_2samp(y, neither)
    xb_result = ks_2samp(x, both)
    yb_result = ks_2samp(y, both)

    results = {
        "id": comparison_id,
        "topics": {"x": X_TOPIC, "y": Y_TOPIC},
        "samples": {
            "x": {"size": len(x),       "avg": int(x_avg),      "avg_date": to_date(x_avg)},
            "y": {"size": len(y),       "avg": int(y_avg),      "avg_date": to_date(y_avg)},
            "both": {"size": len(x),    "avg": int(both_avg),   "avg_date": to_date(both_avg)},
            "neither": {"size": len(x), "avg": int(neither_avg), "avg_date": to_date(neither_avg)},
        },
        "results": {
            "x-y":       {"stat": xy_result.statistic, "pval": xy_result.pvalue, "interpretation": interpret(xy_result)},
            "x-neither": {"stat": xn_result.statistic, "pval": xn_result.pvalue, "interpretation": interpret(xn_result)},
            "y-neither": {"stat": yn_result.statistic, "pval": yn_result.pvalue, "interpretation": interpret(yn_result)},
            "x-both":    {"stat": xb_result.statistic, "pval": xb_result.pvalue, "interpretation": interpret(xb_result)},
            "y-both":    {"stat": yb_result.statistic, "pval": yb_result.pvalue, "interpretation": interpret(yb_result)},
        }
    }
    pprint(results)

    print("WRITING TO FILE...")
    json_filepath = os.path.join(KS_RESULTS_DIR, f"{comparison_id}.json")
    print(json_filepath)
    with open(json_filepath, "w") as f:
        json.dump(results, f)
