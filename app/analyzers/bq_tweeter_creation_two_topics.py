
import os
from pprint import pprint

import numpy as np
from scipy.stats import kstest, ks_2samp
from dotenv import load_dotenv

from app.bq_service import BigQueryService
from app.ks_test_helper import to_dt, to_ts

load_dotenv()
np.random.seed(2020)

X_TOPIC = os.getenv("X_TOPIC", default="#MAGA")
Y_TOPIC = os.getenv("Y_TOPIC", default="#ImpeachAndRemove")

X_LIMIT = int(os.getenv("X_LIMIT", default="1500")) # sample size
Y_LIMIT = int(os.getenv("Y_LIMIT", default="1500")) # sample size

if __name__ == "__main__":

    #
    # Tests whether two independent samples are drawn from the same distribution.
    #
    # Two arrays of sample observations
    # ... assumed to be drawn from a continuous distribution,
    # ... sample sizes can be different.
    #
    # See:
    # ... https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
    # ... https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html
    #

    bq = BigQueryService.cautiously_initialized()

    print(f"FETCHING TWO RANDOM SAMPLES OF TWEETERS BY TOPIC...")
    #print("   X:", X_TOPIC)
    #print("   Y:", Y_TOPIC)
    x_users = list(bq.fetch_random_users(limit=X_LIMIT, topic=X_TOPIC)) # start_at="", end_at=""
    y_users = list(bq.fetch_random_users(limit=Y_LIMIT, topic=Y_TOPIC)) # start_at="", end_at=""

    # is this step necessary from a statistical perspective?
    # or does this confuse independence with exclusivity?
    print("VALIDATING SAMPLES...")
    x_ids = sorted([row.user_id for row in x_users])
    y_ids = sorted([row.user_id for row in y_users])
    common_ids = set(x_ids) & set(y_ids)
    print(f"FOUND {len(common_ids)} COMMON MEMBERS. REMOVING...")
    x_users = [row for row in x_users if row.user_id not in common_ids]
    y_users = [row for row in y_users if row.user_id not in common_ids]

    print("--------------------------")
    print("ANALYZING USER CREATION DATES...")
    x = [to_ts(row.user_created_at) for row in x_users]
    y = [to_ts(row.user_created_at) for row in y_users]

    #print("--------------------------")
    #print("COUNTS...")
    #print("   X:", len(x))
    #print("   Y:", len(y))

    #print("--------------------------")
    #print("AVERAGES...")
    x_avg, y_avg = np.mean(x), np.mean(y)
    #print("   X:", str(to_dt(x_avg)), int(x_avg)) #>
    #print("   Y:", str(to_dt(y_avg)), int(y_avg)) #>

    # print("--------------------------")
    # print("KS TESTS (AGAINST NORMAL DISTRIBUTION)...")
    # print("X:", kstest(x, "norm")) #>
    # print("Y:", kstest(y, "norm")) #>

    print("TWO-SAMPLE KS TEST...")
    ks_result = ks_2samp(x, y)
    #print("   ", ks_result) #> KstestResult(statistic=0.3693181818181818, pvalue=0.041724897141617645)

    #print("--------------------------")
    results = {
        "samples": {
            "x": {"topic": X_TOPIC, "size": len(x), "avg": int(np.mean(x))},
            "y": {"topic": Y_TOPIC, "size": len(y), "avg": int(np.mean(y))},
        },
        "ks2": {"stat": ks_result.statistic, "pval": ks_result.pvalue}
    }
    pprint(results)

    #breakpoint()
