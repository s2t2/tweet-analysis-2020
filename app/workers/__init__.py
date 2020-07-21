
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
DRY_RUN = (os.getenv("DRY_RUN", default="true") == "true")
USERS_LIMIT = os.getenv("USERS_LIMIT")

# @deprecated
def generate_timestamp():
    """Formats datetime for performance logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fmt_ts():
    """
    Formats current timestamp, for printing and logging.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fmt_n(large_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param large_number (int) like 1_000_000_000

    Returns (str) like '1,000,000,000'
    """
    return f"{large_number:,}"

def fmt_pct(decimal_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param decimal_number (float) like 0.95555555555

    Returns (str) like '95.5%'
    """
    return f"{(decimal_number * 100):.2f}%"

def to_ts(my_dt):
    """
    Converts datetime object to timestamp (seconds since epoch).

    Param: dt (datetime) like ... datetime.datetime(2016, 7, 23, 10, 38, 35, 636364)

    Should be inverse of to_dt()
    """
    return int(my_dt.timestamp())

def to_dt(ts):
    """
    Converts timestamp (seconds since epoch) to datetime object.

    Param: dti (int) like ... 1469270315.6363637

    Returns: _______

    Should be inverse of to_ts()
    """
    return datetime.utcfromtimestamp(ts)
