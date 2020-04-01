import os
from datetime import datetime
from dotenv import load_dotenv
from threading import Thread, BoundedSemaphore, current_thread

from app import APP_ENV
from app.storage_service import BigQueryService
from app.twint_scraper import TwitterScraper

load_dotenv()

MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
LIMIT = int(os.getenv("USERS_LIMIT", default=20)) # max number of users to fetch from the db
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=4)) # the max number of users to store in a single BQ call
MAX_THREADS = int(os.getenv("MAX_THREADS", default=3)) # the maximum number of threads to use

def generate_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") # a format for storing in BQ (consider moving)

def split_into_batches(users, batch_size=3):
    # h/t: https://stackoverflow.com/a/8290508/670433
    user_count = len(users)
    for i in range(0, user_count, batch_size):
        print()
        yield users[i: min(i + batch_size, user_count)]

def process_users(users):
    records = []
    for row_index, row in enumerate(users):
        start_at = generate_timestamp()
        print("------------------")
        print(start_at, "|", current_thread(), "|", row_index, "|", row.user_id)

        scraper = TwitterScraper(row.screen_name)
        end_at = generate_timestamp()
        friend_names = sorted(scraper.get_friend_names())
        friend_count = len(friend_names)
        print("FRIENDS COUNT:", friend_count)
        records.append({
            "user_id": row.user_id,
            "screen_name": row.screen_name,
            "verified": row.verified,
            "friend_count": friend_count, # it is possible there could be more than the limit
            "friend_names": friend_names,
            "start_at": start_at,
            "end_at": end_at,
        })

    storable_records = [r for r in records if any(r["friend_names"])] # for now we are not storing friend-less users, so we can go back and try again later
    if any(storable_records):
        print("------------------")
        print(f"SAVING RECORDS (SIZE: {len(storable_records)})...")
        service.append_user_friends(storable_records)

if __name__ == "__main__":

    #for batch in split_into_batches([0,1,2,3,4,5,6,7,8,9,10], 3):
    #    print(batch)
    ##> [0, 1, 2]
    ##> [3, 4, 5]
    ##> [6, 7, 8]
    ##> [9, 10]
    #exit()

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())
    print("DESTRUCTIVE MIGRATIONS:", service.destructive)
    print("VERBOSE QUERIES:", service.verbose)
    print("MIN USER ID:", MIN_ID)
    print("MAX USER ID:", MAX_ID)
    print("USERS LIMIT:", LIMIT)
    print("BATCH SIZE:", BATCH_SIZE)
    print("MAX THREADS:", MAX_THREADS)
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()

    service.init_tables()

    if MIN_ID and MAX_ID:
        users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)
    else:
        users = service.fetch_remaining_users(limit=LIMIT)
    users_count = len(users)
    print("FETCHED", users_count, "USERS")

    pool = BoundedSemaphore(value=MAX_THREADS)
    print(pool)
    with pool:
        for users_batch in split_into_batches(users, BATCH_SIZE):
            Thread(target=process_users, args=([users_batch])).start() # wrap users in a list or else it will try to unpack them and think there are multiple arguments being passed
