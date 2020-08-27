


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




    #with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:
    #    batch = []
    #    lock = BoundedSemaphore()
    #    futures = [executor.submit(user_with_friends, row) for row in users]
    #    print("FUTURE RESULTS", len(futures))
    #    for index, future in enumerate(as_completed(futures)):
    #        result = future.result()
#
    #        lock.acquire()
    #        batch.append(result)
    #        if (len(batch) >= BATCH_SIZE) or (index + 1 >= len(futures)): # when batch is full or is last
    #            print("-------------------------")
    #            print(f"SAVING BATCH OF {len(batch)}...")
    #            print("-------------------------")
    #            service.insert_user_friends(batch)
    #            batch = []
    #        lock.release()



    print("----------------")
    print("ALL PROCESSES COMPLETE!")
    pg_service.close()
