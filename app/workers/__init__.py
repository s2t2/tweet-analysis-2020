
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
DRY_RUN = (os.getenv("DRY_RUN", default="true") == "true")

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