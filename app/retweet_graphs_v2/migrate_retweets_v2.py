

from app.decorators.datetime_decorators import logstamp
from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    print(logstamp())
    bq_service.migrate_populate_retweets_table_v2()
    print(logstamp())

    print("MIGRATION SUCCESSFUL!")
