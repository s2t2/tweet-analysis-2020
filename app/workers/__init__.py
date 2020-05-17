
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
DRY_RUN = (os.getenv("DRY_RUN", default="true") == "true")

def generate_timestamp():
    """Formats datetime for performance logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
