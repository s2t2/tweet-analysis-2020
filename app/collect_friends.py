
from app.storage_service import BigQueryService
from app.twitter_service import twitter_api


if __name__ == "__main__":

    api = twitter_api()
    print("TWITTER API CLIENT", api)

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())

    if input("CONTINUE? (Y/N)").upper() != "Y":
        print("EXITING...")
        exit()

    service.init_tables()

    batch = []
    batch_size = 0
    users = service.fetch_users() # todo: specific ones / join where no matching record in the friends table
    for row in users:
        print("USER:", row.user_id)

        friend_ids = ["101010101", "202020202", "303030303"] # TODO: fetch from twitter

        batch.append({
            "user_id": row.user_id,
            "friends_count": len(friend_ids),
            "friend_ids": friend_ids,
        })

    service.append_user_friends(batch)
