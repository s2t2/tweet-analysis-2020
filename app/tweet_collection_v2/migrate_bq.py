

from app import seek_confirmation
from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_topics_table()
    bq_service.migrate_tweets_table()
