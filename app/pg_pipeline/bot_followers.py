from memory_profiler import profile

from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService

@profile
def perform():

    BATCH_SIZE = 5_000

    pg_service = PgService()

    counter = 0
    edges = set()

    # for each bot:
    bot_id = 123
    bot_screen_name = "ACLU"
    print(logstamp(), "BOT 1 OF 1", bot_screen_name.upper())
    pg_service.fetch_bot_followers_by_screen_name(bot_screen_name)
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch: break

        edges |= set([(row["follower_id"], bot_id) for row in batch])

        counter += len(batch)
        print("  ", logstamp(), fmt_n(counter), "| EDGES:", fmt_n(len(edges)))

    pg_service.close()
    print("COMPLETE!")

if __name__ == "__main__":

    perform()

    #breakpoint()
