import os
from datetime import datetime
from dotenv import load_dotenv
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

from app import APP_ENV
from app.storage_service import BigQueryService
from app.twint_scraper import TwitterScraper

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=10)) # heroku supports max 256, see: https://devcenter.heroku.com/articles/dynos#process-thread-limits
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=5)) # the max number of processed users to store in BQ at once (with a single insert API call)

MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
LIMIT = os.getenv("USERS_LIMIT") # max number of users to fetch from the db

def generate_timestamp():
    """Formats datetime for storing in BigQuery (consider moving)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_friends(row):
    start_at = generate_timestamp()
    print(start_at, "|", current_thread().name, "|", row.user_id)
    scraper = TwitterScraper(row.screen_name)
    end_at = generate_timestamp()
    friend_names = sorted(scraper.get_friend_names())
    print(start_at, "|", current_thread().name, "|", row.user_id, "FRIENDS:", len(friend_names))
    return {
        "user_id": row.user_id,
        "screen_name": row.screen_name,
        "verified": row.verified,
        "friend_count": len(friend_names),
        "friend_names": friend_names,
        "start_at": start_at,
        "end_at": end_at
    }

if __name__ == "__main__":

    service = BigQueryService()
    print("-------------------------")
    print("BIGQUERY DATASET:", service.dataset_address.upper())
    print("DESTRUCTIVE MIGRATIONS:", service.destructive)
    print("VERBOSE QUERIES:", service.verbose)
    print("-------------------------")
    print("MIN USER ID:", MIN_ID)
    print("MAX USER ID:", MAX_ID)
    print("USERS LIMIT:", LIMIT)
    print("-------------------------")
    print("MAX THREADS:", MAX_THREADS)
    print("BATCH SIZE:", BATCH_SIZE)
    print("-------------------------")
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()
    service.init_tables()

    users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)
    print("FETCHED UNIVERSE OF", len(users), "USERS")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
        futures = [executor.submit(fetch_friends, row) for row in users]
        print("FUTURE RESULTS", len(futures))
        batch = []
        for index, future in enumerate(as_completed(futures)):
            result = future.result()
            #print(result)

            # this results in all the first few having zero on the next run, so let's just store them
            # if any(result["friend_names"]):
            #     batch.append(result)
            batch.append(result)

            # store full batch or when there are no more left to store...
            if (len(batch) >= BATCH_SIZE) or (index + 1 >= len(futures)):
                print("-------------------------")
                print(f"SAVING BATCH OF {len(batch)}...")
                print("-------------------------")
                service.append_user_friends(batch)
                batch = []
