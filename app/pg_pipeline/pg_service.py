
from psycopg2 import connect
from psycopg2.extras import DictCursor

from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import logstamp

from app.pg_pipeline.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME

class PgService:
    def __init__(self, database_url=DATABASE_URL):
        self.database_url = database_url
        self.connection = connect(self.database_url)
        self.cursor = self.connection.cursor(name="pg_service_cursor", cursor_factory=DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!

        print("-------------------------")
        print("PG SERVICE")
        print(f"  DATABASE URL: '{self.database_url}'")
        print("  CONNECTION:", type(self.connection))
        print("  CURSOR:", type(self.cursor), self.cursor.name)

    def close(self):
        """Call this when done using the cursor."""
        print("CLOSING PG CONNECTION...")
        self.cursor.close()
        self.connection.close()

    def fetch_user_friends(self, limit=None):
        sql = f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {USER_FRIENDS_TABLE_NAME} "
        if limit:
            sql += f" LIMIT {int(limit)};"
        self.cursor.execute(sql)


if __name__ == "__main__":

    LIMIT = 100_000
    BATCH_SIZE = 10_000

    pg_service = PgService()

    counter = 0
    pg_service.fetch_user_friends(limit=LIMIT)
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch: break
        counter += len(batch)
        print(logstamp(), fmt_n(counter))

    pg_service.close()
    print("COMPLETE!")
