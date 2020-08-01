
import os
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
DRY_RUN = (os.getenv("DRY_RUN", default="true") == "true")
USERS_LIMIT = os.getenv("USERS_LIMIT")
