

from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_populate_user_details_table_v2()

    print("MIGRATION SUCCESSFUL!")
