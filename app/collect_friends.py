
from app.storage_service import BigQueryService
from app.twitter_service import twitter_api







if __name__ == "__main__":

    api = twitter_api()
    print("TWITTER API CLIENT", api)

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())

    service.migrate_users()

    users = service.fetch_users()
    for row in users:
        print("USER:", row.user_id)

    #friendless_users = service.fetch_friendless_users(limit=20)
#
    #for row in friendless_users:
    #    print("USER:", row.user_id)
#
    #    friend_ids = [101010101, 202020202, 303030303] # TODO: fetch from twitter
    #    breakpoint()
    #    #service.update_user_friends(row.user_id, friend_ids)
