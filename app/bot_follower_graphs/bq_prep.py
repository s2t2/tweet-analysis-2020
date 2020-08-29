
from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService(verbose=True)

    print("FLATTENING USER FRIENDS TABLE...")
    bq_service.destructively_migrate_user_friends_flat()

    print("BOTS ABOVE 80...")
    bq_service.destructively_migrate_bots_table()

    print("BOT FOLLOWERS ABOVE 80...")
    bq_service.destructively_migrate_bot_followers_table()
