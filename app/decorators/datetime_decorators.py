
from datetime import datetime, timezone

def logstamp():
    """
    Formats current timestamp, for printing and logging.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def to_ts(dt):
    """
    Converts datetime object to UTC timestamp (seconds since epoch) like 1595759389.828663. Inverse of to_dt() function.

    Params: dt (datetime) like ... datetime(2020, 7, 26, 10, 29, 49, 828663)
    """
    return dt.replace(tzinfo=timezone.utc).timestamp()

def to_dt(ts):
    """
    Converts UTC timestamp (seconds since epoch) to datetime object like datetime(2020, 7, 26, 10, 29, 49, 828663). Inverse of to_ts() function.

    Params: ts (float) seconds since epoch (like 1595759389.828663)
    """
    return datetime.utcfromtimestamp(ts)

def fmt_date(ts):
    """
    Converts timestamp (seconds since epoch) to date string object like "2014-02-10".

    Params: ts (float) seconds since epoch (like 1595759389.828663)
    """
    return to_dt(ts).strftime("%Y-%m-%d")
