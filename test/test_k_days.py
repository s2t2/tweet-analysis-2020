
from datetime import datetime

from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator

def test_date_ranges():

    gen = DateRangeGenerator(start_date="2020-01-01", k_days=3, n_periods=5)
    assert [{"start_at": dr.start_at, "end_at": dr.end_at} for dr in gen.date_ranges] == [
        {'start_at': datetime(2020, 1, 1, 0, 0),  'end_at': datetime(2020, 1, 3, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 4, 0, 0),  'end_at': datetime(2020, 1, 6, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 7, 0, 0),  'end_at': datetime(2020, 1, 9, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 10, 0, 0), 'end_at': datetime(2020, 1, 12, 23, 59, 59)},
        {'start_at': datetime(2020, 1, 13, 0, 0), 'end_at': datetime(2020, 1, 15, 23, 59, 59)}
    ]
