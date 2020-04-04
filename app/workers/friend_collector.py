
import os
from datetime import datetime
from dotenv import load_dotenv
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

from app import APP_ENV
from app.storage_service import BigQueryService, generate_timestamp
from app.twitter_scraper import get_friends, VERBOSE_SCRAPER, MAX_FRIENDS

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=10)) # the max number of threads to use, for concurrent processing
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=20)) # the max number of processed users to store in BQ at once (with a single insert API call)

MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
LIMIT = os.getenv("USERS_LIMIT") # max number of users to fetch from the db

#VERBOSE_COLLECTOR = os.getenv("VERBOSE_COLLECTOR", default="true") == "true"

def user_with_friends(row):
    start_at = generate_timestamp()
    print(f"{start_at} | {current_thread().name} | {row.user_id}")

    friend_names = sorted(get_friends(row.screen_name))
    end_at = generate_timestamp()
    print(f"{end_at} | {current_thread().name} | {row.user_id} | FRIENDS: {len(friend_names)}")

    return {
        "user_id": row.user_id,
        "screen_name": row.screen_name,
        "friend_count": len(friend_names),
        "friend_names": friend_names,
        "start_at": start_at,
        "end_at": end_at
    }

def cautiously_initialized_storage_service():
    service = BigQueryService()
    print("-------------------------")
    print("DB CONFIG...")
    print("  BIGQUERY DATASET:", service.dataset_address.upper())
    print("  DESTRUCTIVE MIGRATIONS:", service.destructive)
    print("  VERBOSE QUERIES:", service.verbose)
    print("-------------------------")
    print("WORKER CONFIG...")
    print("  MIN USER ID:", MIN_ID)
    print("  MAX USER ID:", MAX_ID)
    print("  USERS LIMIT:", LIMIT)
    print("  MAX THREADS:", MAX_THREADS)
    print("  BATCH SIZE:", BATCH_SIZE)
    print("-------------------------")
    print("SCRAPER CONFIG...")
    print("  VERBOSE SCRAPER:", VERBOSE_SCRAPER)
    print("  MAX FRIENDS:", MAX_FRIENDS)
    print("-------------------------")
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()
    service.init_tables()
    return service

if __name__ == "__main__":

    service = cautiously_initialized_storage_service()

    users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)
    print("FETCHED UNIVERSE OF", len(users), "USERS")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
        batch = []
        lock = BoundedSemaphore()
        futures = [executor.submit(user_with_friends, row) for row in users]
        print("FUTURE RESULTS", len(futures))
        for index, future in enumerate(as_completed(futures)):
            result = future.result()

            # OK, so this locking business:
            # ... prevents random threads from clearing the batch, which was causing results to almost never get stored, and
            # ... restricts a thread's ability to acquire access to the batch until another one has released it
            lock.acquire()
            batch.append(result)
            if (len(batch) >= BATCH_SIZE) or (index + 1 >= len(futures)): # when batch is full or is last
                print("-------------------------")
                print(f"SAVING BATCH OF {len(batch)}...")
                print("-------------------------")
                service.append_user_friends(batch)
                batch = []
            lock.release()
