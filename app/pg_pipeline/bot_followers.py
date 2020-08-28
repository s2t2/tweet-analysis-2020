from memory_profiler import profile

from app import seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService

BATCH_SIZE = 100
BOT_MIN = 0.8

@profile
def perform():
    pg_service = PgService()

    print("FETCHING BOT FOLLOWERS...")
    pg_service.fetch_bots_with_followers(bot_min=BOT_MIN)

    row_counter = 0
    edge_counter = 0
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch: break
        for row in batch:
            bot_id = row["bot_id"]
            #print(len(row["follower_ids"]))
            edges = [(follower_id, bot_id) for follower_id in row["follower_ids"]]
            edge_counter += len(edges)

        row_counter += len(batch)
        print("  ", logstamp(), "| BOTS:", fmt_n(row_counter), "| EDGES:", fmt_n(edge_counter))

    pg_service.close()
    print("COMPLETE!")

if __name__ == "__main__":

    perform()

    #breakpoint()
