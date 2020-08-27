from memory_profiler import profile

from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.pg_pipeline.pg_service import PgService

@profile
def perform():

    BATCH_SIZE = 500

    pg_service = PgService()

    sql = f"""
        SELECT
            b.user_id
            ,sn.screen_name
            ,COUNT(DISTINCT uf.user_id) as follower_count
            ,ARRAY_AGG(DISTINCT uf.user_id) as follower_ids
        FROM (
            SELECT user_id, count(start_date) as day_count
            FROM daily_bot_probabilities
            WHERE bot_probability >= 0.8
            GROUP BY 1
            -- ORDER BY 2 DESC
        ) b -- 24,150
        LEFT JOIN user_screen_names sn ON sn.user_id = b.user_id -- 24,150
        LEFT JOIN user_friends uf ON sn.screen_name ILIKE ANY(uf.friend_names)
        GROUP BY 1,2
        -- ORDER BY 2 DESC
    """
    pg_service.cursor.execute(sql)

    counter = 0
    edges = set()
    while True:
        batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)
        if not batch: break

        #edges |= set([(row["follower_id"], bot_id) for row in batch])

        counter += len(batch)
        print("  ", logstamp(), fmt_n(counter), "| EDGES:", fmt_n(len(edges)))

    pg_service.close()
    print("COMPLETE!")

if __name__ == "__main__":

    perform()

    #breakpoint()
