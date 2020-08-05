
from datetime import datetime

from app.decorators.datetime_decorators import logstamp, dt_to_date, dt_to_s, s_to_dt
from app.decorators.datetime_decorators import to_ts as dt_to_ts
from app.decorators.datetime_decorators import fmt_date as ts_to_date
from app.decorators.datetime_decorators import to_dt as ts_to_dt


dt = datetime(2020, 7, 26, 10, 29, 49, 828663)
ts = 1595759389.828663
s = "2020-07-26 10:29:49"

def test_logstamp():
    # this test might fail if run right when the day changes.
    # the point is it contains the current datetime info...
    logstr = logstamp()
    assert isinstance(logstr, str)
    assert str(datetime.now().year) in logstr
    assert str(datetime.now().month) in logstr
    assert str(datetime.now().day) in logstr


def test_datetime_decorators():
    assert dt_to_date(dt) == '2020-07-26'
    assert dt_to_s(dt) == s
    assert dt_to_ts(dt) == ts

def test_timestamp_decorators():
    assert ts_to_date(ts) == '2020-07-26'
    assert ts_to_dt(ts) == dt

def test_string_decorators():
    assert s_to_dt(s) == dt.replace(microsecond = 0)

def test_inverse_conversions():
    # we should be able to convert a timestamp to a date-time and then back again and it should be the same thing
    assert dt_to_ts(dt) == ts
    assert ts_to_dt(ts) == dt

    # strings and datetime objects
    assert dt_to_s(s_to_dt(s)) == s
