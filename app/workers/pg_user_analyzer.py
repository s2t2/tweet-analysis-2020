
#from datetime import datetime as dt

import numpy as np
from scipy.stats import kstest, ks_2samp

from app.models import db, BoundSession, UserDetail, USER_DETAILS_TABLE_NAME

np.random.seed(99)

if __name__ == "__main__":
    #
    # GET ALL CREATED AT DATES (WITH SAMPLE LABELS)
    #
    # users = [
    #     {"created_at":"2012-01-01", "community": "X"}
    #     {"created_at":"2013-01-01", "community": "X"},
    #     {"created_at":"2018-01-01", "community": "X"},
    #     {"created_at":"2017-01-01", "community": "Y"},
    #     {"created_at":"2017-01-02", "community": "Y"},
    #     {"created_at":"2017-01-03", "community": "Y"},
    # ]
    # x = [_______ for u in users if u["community"] == "X"]
    # y = [_______ for u in users if u["community"] == "Y"]

    #session = BoundSession()
    #rows = session.query(UserDetail).values("user_id", "screen_name", "created_at").limit(10)
    #for row in rows:
    #    print("...", row.user_id, "|", row.screen_name, "|", row.created_at)
    #session.close()
    #exit()

    sql = f"""
        SELECT user_id, created_at
        FROM {USER_DETAILS_TABLE_NAME}
        LIMIT 10
    """
    results = db.execute(sql)
    rows = results.fetchall()

    timestamps = [int(row.created_at.timestamp()) for row in rows]
    print(min(timestamps), max(timestamps))

    # TODO: ks tests
