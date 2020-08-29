
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n

from app.pg_pipeline.pg_service import PgService

def fetch_in_batches():
    pg_service = PgService()
    pg_service.cursor.execute("SELECT user_id, screen_name, friend_count FROM user_friends LIMIT 1000;")
    while True:
        batch = pg_service.cursor.fetchmany(size=100)
        if batch:
            yield batch
        else:
            break
    pg_service.close()
    print("COMPLETE!")

def batch_perform():
    counter = 0
    for batch in fetch_in_batches():
        counter += len(batch)
        print(logstamp(), fmt_n(counter))

#

def execute_query(sql):
    pg_service = PgService()
    pg_service.cursor.execute(sql)
    yield from pg_service.cursor.fetchall() # yield happens to wrap the list in another list (because the fetchall is already a generator, so we can "yield from" it)
    pg_service.close()
    print("COMPLETE!")

def perform():
    generator = execute_query("SELECT user_id, screen_name, friend_count FROM user_friends LIMIT 100;")
    results = list(generator)
    print(logstamp(), fmt_n(len(results)))


if __name__ == "__main__":

    batch_perform()
    #> 2020-08-29 09:44:16 100
    #> 2020-08-29 09:44:16 200
    #> 2020-08-29 09:44:16 300
    #> 2020-08-29 09:44:16 400
    #> 2020-08-29 09:44:16 500
    #> 2020-08-29 09:44:16 600
    #> 2020-08-29 09:44:16 700
    #> 2020-08-29 09:44:16 800
    #> 2020-08-29 09:44:16 900
    #> 2020-08-29 09:44:16 1,000
    #> CLOSING PG CONNECTION...
    #> COMPLETE!

    #perform()
    #> CLOSING PG CONNECTION...
    #> COMPLETE!
    #> 2020-08-29 09:51:55 100
