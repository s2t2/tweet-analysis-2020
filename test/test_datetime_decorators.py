
from datetime import datetime

from app.datetime_decorators import to_ts, to_dt

def test_bidirectional_timestamp_conversion():

    dt = datetime(2020, 7, 26, 10, 29, 49, 828663)
    ts = 1595759389.828663

    assert to_ts(dt) == ts
    assert to_dt(ts) == dt
