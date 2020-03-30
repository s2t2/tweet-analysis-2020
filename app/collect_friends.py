
from app.storage_service import BigQueryService
from app.twitter_service import twitter_faster_api, get_friends

UNIVERSE_SIZE = 450
BATCH_SIZE = 200
MAX_FRIENDS = 2000

if __name__ == "__main__":

    api = twitter_faster_api()
    print("TWITTER API CLIENT", api)

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())

    if input("CONTINUE? (Y/N): ").upper() != "Y":
        print("EXITING...")
        exit()

    service.init_tables()

    users = service.fetch_remaining_users(limit=UNIVERSE_SIZE)
    users_count = len(users)
    print("FETCHED", users_count, "USERS...")

    batch = []
    for row_index, row in enumerate(users):
        print("INDEX:", row_index) # starts at zero
        print("USER:", row.user_id)

        friend_ids = get_friends(user_id=row.user_id, max_friends=MAX_FRIENDS)

        batch.append({
            "user_id": row.user_id,
            "friends_count": len(friend_ids),
            "friend_ids": friend_ids,
        })

        # store full batches, and the final batch, even if the final batch isn't full
        if (len(batch) >= BATCH_SIZE) or (row_index + 1 >= users_count):
            print(f"SAVING AND CLEARING THE BATCH (SIZE: {batch_size})...")
            service.append_user_friends(batch)
            batch = []
            batch_size = 0
