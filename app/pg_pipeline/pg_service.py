
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
        #self.named_cursor = self.connection.cursor(name="pg_service_cursor", cursor_factory=DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!
        #self.cursor = self.connection.cursor(cursor_factory=DictCursor) # no name cursor can execute more than one query

        print("-------------------------")
        print("PG SERVICE")
        print(f"  DATABASE URL: '{self.database_url}'")
        print("  CONNECTION:", type(self.connection))
        print("  CURSOR:", type(self.cursor), self.cursor.name)

    #def reset_named_cursor(self, cursor_name="pg_service_cursor"):
    #    # Get around psycopg2.ProgrammingError: can't call .execute() on named cursors more than once
    #    # ... or just ditch the named cursor
    #    self.named_cursor = None
    #    self.named_cursor = self.connection.cursor(name=cursor_name, cursor_factory=DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!

    def close(self):
        """Call this when done using the cursor."""
        print("CLOSING PG CONNECTION...")
        self.cursor.close()
        self.connection.close()

    def get_user_friends(self, limit=None):
        sql = f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {USER_FRIENDS_TABLE_NAME} "
        if limit:
            sql += f" LIMIT {int(limit)};"
        self.cursor.execute(sql)

    def get_bot_followers(self, limit=None, bot_min=0.8):
        #bot_min_str = str(int(bot_min * 100)) #> "80"
        sql = f"""
            SELECT bot_id, ARRAY_AGG(distinct follower_user_id) as follower_ids
            FROM bot_followers_above_80
            GROUP BY 1
        """ # takes 90 seconds for ~25K rows
        if limit:
            sql += f" LIMIT {int(limit)};"
        self.cursor.execute(sql)


if __name__ == "__main__":

    LIMIT = 100_000
    BATCH_SIZE = 10_000

    pg_service = PgService()

    counter = 0
    pg_service.get_user_friends(limit=LIMIT)
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch: break
        counter += len(batch)
        print(logstamp(), fmt_n(counter))

    pg_service.close()
    print("COMPLETE!")
