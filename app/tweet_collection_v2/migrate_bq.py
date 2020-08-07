

from app import seek_confirmation
from app.bq_service import BigQueryService
from app.tweet_collection_v2.csv_storage import LocalStorageService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_topics_table()
    bq_service.migrate_tweets_table()

    print("--------------------")
    print("SEEDING TOPICS...")
    local_storage = LocalStorageService()
    topics = local_storage.fetch_topic_names()
    bq_service.append_topics(topics)
