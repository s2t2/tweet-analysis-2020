import os
from datetime import datetime
from dotenv import load_dotenv
from threading import Thread, BoundedSemaphore, current_thread

from app import APP_ENV
from app.storage_service import BigQueryService
from app.twint_scraper import TwitterScraper

load_dotenv()

#MAX_THREADS = int(os.getenv("MAX_THREADS", default=3)) # the maximum number of threads to use. each thread will process a batch of the specified size
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=4)) # the max number of processed users to store in BQ at once (with a single insert API call)
# optional:
MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
LIMIT = os.getenv("USERS_LIMIT") # max number of users to fetch from the db

def generate_timestamp():
    """Formats datetime for storing in BigQuery (consider moving)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def split_into_batches(users, batch_size=3):
    """
    A generator to split list into batches of the specified size
        h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """
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
        print(f"SAVING RECORDS (SIZE: {len(storable_records)}) {current_thread()}...")
        service.append_user_friends(storable_records)

if __name__ == "__main__":

    service = BigQueryService()

    print("BIGQUERY DATASET:", service.dataset_address.upper())
    print("DESTRUCTIVE MIGRATIONS:", service.destructive)
    print("VERBOSE QUERIES:", service.verbose)
    print("MIN USER ID:", MIN_ID)
    print("MAX USER ID:", MAX_ID)
    print("USERS LIMIT:", LIMIT)
    #print("MAX THREADS:", MAX_THREADS)
    print("BATCH SIZE:", BATCH_SIZE)
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()

    service.init_tables()

    users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID, limit=LIMIT)
    print("FETCHED UNIVERSE OF", len(users), "USERS")

    # not sure if this MAX_THREADS approach applies in a non-DB environment?
    #
    # pool = BoundedSemaphore(value=MAX_THREADS)
    # print(pool)
    # with pool:
    #     for users_batch in split_into_batches(users, BATCH_SIZE):
    #         Thread(target=process_users, args=([users_batch])).start() # wrap users in a list or else it will try to unpack them and think there are multiple arguments being passed

    for users_batch in split_into_batches(users, BATCH_SIZE):
        Thread(target=process_users, args=([users_batch])).start() # wrap users in a list or else it will try to unpack them and think there are multiple arguments being passed
