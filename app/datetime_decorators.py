
from datetime import datetime, timezone

def to_ts(dt):
    """
    Converts datetime object to timestamp (seconds since epoch). Should be inverse of to_dt().

    Param: dt (datetime) like ... datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)

    Returns: (float) like ... 1469270315.6363637
    """
    #return dt.timestamp()
    return dt.replace(tzinfo=timezone.utc).timestamp()

def to_dt(ts):
    """
    Converts timestamp (seconds since epoch) to datetime object. Should be inverse of to_ts().

    Param: ts (float) seconds since epoch like ... 1469270315.6363637

    Returns: (datetime) like ... datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)
    """
    return datetime.utcfromtimestamp(ts)

def fmt_date(ts):
    """
    Converts timestamp (seconds since epoch) to date string object.

    Param: ts (float) seconds since epoch like ... 1469270315.6363637

    Returns: (str) like ... "2014-02-10"
    """
    return to_dt(ts).strftime("%Y-%m-%d")
