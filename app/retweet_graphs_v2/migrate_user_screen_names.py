

from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    bq_service.migrate_populate_user_screen_names_table()

    print("MIGRATION SUCCESSFUL!")
