from memory_profiler import profile

from app import seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService

BATCH_SIZE = 5_000
BOT_MIN = 0.8

@profile
def perform():

    pg_service = PgService()

    #seek_confirmation()
    # TODO: destructively migrate bot followers table

    print("FETCHING BOTS...")
    pg_service.fetch_bots(bot_min=BOT_MIN)
    bots = pg_service.cursor.fetchall()
    bot_count = len(bots)
    print(bot_count)

    print("FINDING THEIR FOLLOWERS...")
    for bot_counter, bot in enumerate(bots):
        print(logstamp(), f"BOT {bot_counter} OF {bot_count}:", bot["bot_screen_name"])

        counter = 0
        #pg_service.fetch_bot_followers_by_screen_name(bot["bot_screen_name"])
        #while True:
        #    batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        #    if not batch: break
#
        #    # TODO: insert into a table... set([(row["follower_id"], bot["bot_id"]) for row in batch])
#
        #    counter += len(batch)
        #    print("  ", logstamp(), "| FOLLOWERS:", fmt_n(counter))

    pg_service.close()
    print("COMPLETE!")

if __name__ == "__main__":

    perform()

    #breakpoint()
