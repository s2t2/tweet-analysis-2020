import os
from datetime import datetime
from dotenv import load_dotenv

from app.storage_service import BigQueryService
from app.twint_scraper import TwitterScraper

load_dotenv()

LIMIT = int(os.getenv("USERS_LIMIT", default=10)) # max number of users to fetch from the db (otherwise specify partition via min and max ids)
MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=4)) # the number of users to store in a single BQ call

def generate_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") # a format for storing in BQ (consider moving)

if __name__ == "__main__":

    #
    # FETCH USERS
    #

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())

    if input("CONTINUE? (Y/N): ").upper() != "Y":
        print("EXITING...")
        exit()
    service.init_tables()

    if MIN_ID and MAX_ID:
        print("MIN USER ID:", MIN_ID)
        print("MAX USER ID:", MAX_ID)
        users = service.fetch_remaining_users(min_id=MIN_ID, max_id=MAX_ID)
    else:
        print("USERS LIMIT:", LIMIT)
        users = service.fetch_remaining_users(limit=LIMIT)
    users_count = len(users)
    print("FETCHED", users_count, "USERS...")

    #
    # PROCESS USERS
    #

    print("PROCESSING USERS IN BATCHES OF:", BATCH_SIZE)
    batch = []
    batch_size = 0
    for row_index, row in enumerate(users):
        print("------------------")
        start_at = generate_timestamp()
        print(start_at, "|", row_index, "|", row.user_id)

        #
        # GET FRIENDS
        #

        scraper = TwitterScraper(row.screen_name)
        friend_names = sorted(scraper.get_friend_names())
        friend_count = len(friend_names)
        if any(friend_names):
            print("FRIENDS COUNT:", friend_count)
            batch.append({
                "user_id": row.user_id,
                "screen_name": row.screen_name,
                "verified": row.verified,
                "friend_count": friend_count, # it is possible there could be more than the limit
                "friend_names": friend_names,
                "start_at": start_at,
                "end_at": generate_timestamp(),
            })
            batch_size += 1

        #
        # STORE USERS AND FRIENDS
        #

        # store full batches, and the final batch, even if the final batch isn't full:
        if (batch_size >= BATCH_SIZE) or (row_index + 1 >= users_count):
            print("------------------")
            print(f"SAVING BATCH (SIZE: {batch_size})...")
            service.append_user_friends(batch)
            print(f"CLEARING BATCH...")
            batch = []
            batch_size = 0
