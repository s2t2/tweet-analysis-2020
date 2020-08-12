

from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_daily_bot_probabilities_table()

    print("MIGRATION SUCCESSFUL!")
