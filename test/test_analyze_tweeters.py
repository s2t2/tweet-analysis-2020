
from datetime import datetime

from app.workers.bq_analyze_tweeters_by_topic import to_dt

def test_removal_of_common_items():
    x_ids = ["1111", "2222", "3333", "4444"]
    y_ids = ["5555", "2222", "6666", "7777"]

    common_ids = (set(x_ids) & set(y_ids)) # h/t: https://www.geeksforgeeks.org/python-check-two-lists-least-one-element-common/
    assert common_ids == {"2222"}

    x_ids = list(set(x_ids) - common_ids)
    assert x_ids == ["1111", "3333", "4444"]

mock_dt = datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)
mock_ts = 1469270315.6363637

def test_timestamp_conversion():
    assert to_ts(mock_dt) == mock_ts

def test_timestamp_inversion():
    assert to_dt(mock_ts) == mock_dt
