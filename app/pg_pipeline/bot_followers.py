from memory_profiler import profile

from app import seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService

BATCH_SIZE = 25_000
BOT_MIN = 0.8

@profile
def perform():

    pg_service = PgService()

    print("FETCHING BOT FOLLOWERS...")
    pg_service.fetch_bot_followers(bot_min=BOT_MIN)

    counter = 0
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch:
            break

        #breakpoint()
        # TODO: insert into a table... set([(row["follower_id"], bot["bot_id"]) for row in batch])

        counter += len(batch)
        print("  ", logstamp(), "| EDGES:", fmt_n(counter))

    pg_service.close()
    print("COMPLETE!")

if __name__ == "__main__":

    perform()

    #breakpoint()
