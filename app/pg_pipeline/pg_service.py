
from psycopg2 import connect
from psycopg2.extras import DictCursor

from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import logstamp

from app.pg_pipeline.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME

class PgService:
    def __init__(self, database_url=DATABASE_URL):
        self.database_url = database_url
        self.connection = connect(self.database_url)
        #self.named_cursor = self.connection.cursor(name="pg_service_cursor", cursor_factory=DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!
        self.cursor = self.connection.cursor(cursor_factory=DictCursor) # no name cursor can execute more than one query

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

    def fetch_user_friends(self, limit=None):
        sql = f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {USER_FRIENDS_TABLE_NAME} "
        if limit:
            sql += f" LIMIT {int(limit)};"
        self.cursor.execute(sql)

    def fetch_bots(self, bot_min=0.8):
        sql = f"""
            SELECT
                b.user_id as bot_id
                ,sn.screen_name as bot_screen_name
                ,b.day_count
                ,b.avg_daily_score
            FROM (
                SELECT user_id, count(start_date) as day_count, avg(bot_probability) as avg_daily_score
                FROM daily_bot_probabilities
                WHERE bot_probability >= {float(bot_min)}
                GROUP BY 1
                -- HAVING count(start_date) >= 2 -- 16,087
                ORDER BY 2 desc
            ) b -- 24,150
            JOIN user_screen_names sn on sn.user_id = b.user_id -- 24,973 rows (some ids with many sns, and vice versa)
            ORDER BY 3 desc
        """
        self.cursor.execute(sql)
        #return pg_service.cursor.fetchall()

    def fetch_bot_followers_by_screen_name(self, bot_screen_name):
        """
        For a given user screen name, returns a list of their followers.
        Based on data collected during friend collection, where friends are limited to 2000, so results may not be entirely comprehensive.
        """
        sql = f"""
            SELECT
                -- '{bot_screen_name.upper()}' as bot_screen_name
                user_id as follower_id
                ,screen_name as follower_screen_name
                --,friend_count
                --,friend_names
            FROM user_friends
            WHERE '{bot_screen_name}' ilike any(friend_names)
        """
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
