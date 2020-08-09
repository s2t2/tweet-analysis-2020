
from datetime import datetime

from app.retweet_graphs_v2.k_days_grapher import get_date_ranges

def test_date_ranges():
    assert get_date_ranges(start_date="2020-01-01", k_days=3, n_periods=5) == [
        {'start_at': datetime(2020, 1, 1, 0, 0),  'end_at': datetime(2020, 1, 3, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 4, 0, 0),  'end_at': datetime(2020, 1, 6, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 7, 0, 0),  'end_at': datetime(2020, 1, 9, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 10, 0, 0), 'end_at': datetime(2020, 1, 12, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 13, 0, 0), 'end_at': datetime(2020, 1, 15, 23, 59, 59)}
    ]
