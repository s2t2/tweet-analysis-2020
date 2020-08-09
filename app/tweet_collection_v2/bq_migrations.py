

from pprint import pprint

from app import seek_confirmation
from app.decorators.datetime_decorators import dt_to_s
from app.bq_service import BigQueryService
from app.tweet_collection_v2.csv_storage import LocalStorageService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_topics_table()

    print("--------------------")
    print("SEEDING TOPICS...")
    local_storage = LocalStorageService()
    topics = local_storage.fetch_topic_names()

    bq_service.append_topics(topics)

    for row in bq_service.fetch_topics():
        print(row.topic, "|", dt_to_s(row.created_at))

    seek_confirmation()
    if bq_service.destructive:
        input(f"THIS WILL DESTROY THE TWEETS TABLE ON '{bq_service.dataset_address.upper()}'. ARE YOU REALLY SURE YOU WANT TO DO THIS?")
    bq_service.migrate_tweets_table()
