
from datetime import datetime, timezone

def logstamp():
    """
    Formats current timestamp, for printing and logging.
    """
    return dt_to_s(datetime.now())

#
# DATETIME DECORATORS
#

def dt_to_s(dt):
    """
    Converts datetime object to date string like "2020-01-01 00:00:00"

    Params: dt (datetime) like ... datetime(2020, 7, 26, 10, 29, 49, 828663)
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def dt_to_date(dt):
    """
    Converts datetime object to date string object like "2014-02-10".

    Params: dt (datetime) like ... datetime(2020, 7, 26, 10, 29, 49, 828663)
    """
    return dt.strftime("%Y-%m-%d")

def to_ts(dt): # todo: replace references with dt_to_ts
    """
    Converts datetime object to UTC timestamp (seconds since epoch) like 1595759389.828663. Inverse of to_dt() function.

    Params: dt (datetime) like ... datetime(2020, 7, 26, 10, 29, 49, 828663)
    """
    return dt.replace(tzinfo=timezone.utc).timestamp()

def dt_to_ts(dt):
    return to_ts(dt)

#
# TIMESTAMP DECORATORS
#

def fmt_date(ts): # todo: rename as ts_to_date
    """
    Converts timestamp (seconds since epoch) to date string object like "2014-02-10".

    Params: ts (float) seconds since epoch (like 1595759389.828663)
    """
    return dt_to_date(to_dt(ts))

def to_dt(ts): # todo: rename as ts_to_dt
    """
    Converts UTC timestamp (seconds since epoch) to datetime object like datetime(2020, 7, 26, 10, 29, 49, 828663). Inverse of to_ts() function.

    Params: ts (float) seconds since epoch (like 1595759389.828663)
    """
    return datetime.utcfromtimestamp(ts)

#
# STRING DECORATORS
#

def s_to_dt(s):
    """
    Converts date string to datetime object

    Params: s (str) like ... "2020-01-01 00:00:00"
    """
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def s_to_date(s):
    return dt_to_date(s_to_dt(s))

def date_to_dt(date):
    return datetime.strptime(date, "%Y-%m-%d")

def date_to_ts(date):
    """
    Converts datetime object to UTC timestamp (seconds since epoch) like 1329609600.0

    Params: date (str) like "2020-01-01"
    """
    return dt_to_ts(date_to_dt(date))
