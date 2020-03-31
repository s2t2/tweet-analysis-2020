import os
from datetime import datetime
from dotenv import load_dotenv

from app.storage_service import BigQueryService
from app.twitter_service import twitter_api, get_friends

load_dotenv()

LIMIT = int(os.getenv("USERS_LIMIT", default=10)) # max number of users to fetch from the db (otherwise specify partition via min and max ids)
MIN_ID = os.getenv("MIN_USER_ID") # if partitioning users, the lower bound of the partition
MAX_ID = os.getenv("MAX_USER_ID") # if partitioning users, the upper bound of the partition
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=4)) # the number of users to store in a single BQ call
MAX_FRIENDS = int(os.getenv("MAX_FRIENDS", default=2000)) # the max number of friends to get for each user

if __name__ == "__main__":

    api = twitter_api()
    print("TWITTER API CLIENT", api)

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
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", row_index, "|", row.user_id)

        #
        # GET FRIENDS
        #

        friend_ids = get_friends(user_id=row.user_id, max_friends=MAX_FRIENDS)
        batch.append({
            "user_id": row.user_id,
            "friends_count": len(friend_ids), # it is possible there could be more than the limit
            "friend_ids": friend_ids,
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
            batch = []
            batch_size = 0
            print(f"CLEARING BATCH...")
