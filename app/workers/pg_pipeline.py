
import time
import os
from dotenv import load_dotenv

from app.models import UserFriend, BoundSession, db
from app.storage_service import BigQueryService, generate_timestamp, bigquery

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100)) # use 1,000 or 10,000 in production
DESTRUCTIVE_PG = (os.getenv("DESTRUCTIVE_PG", default="false") == "true")

class Pipeline():
    def __init__(self, batch_size=BATCH_SIZE, bq=None):
        print("-------------------------")
        print("PG PIPELINE...")
        self.batch_size = batch_size
        print("  BATCH SIZE:", self.batch_size)
        self.bq = (bq or BigQueryService.cautiously_initialized())
        #self.db = db

    def perform(self):
        self.start_at = time.perf_counter()
        self.session = BoundSession()
        self.batch = []
        self.counter = 0

        for row in self.bq.fetch_user_friends_in_batches():
            self.batch.append({
                "user_id": row["user_id"],
                "screen_name": row["screen_name"],
                "friend_count": row["friend_count"],
                "friend_names": row["friend_names"]
            })
            self.counter+=1

            if self.counter % self.batch_size == 0:
                print(generate_timestamp(), self.counter, "SAVING BATCH...")
                self.session.bulk_insert_mappings(UserFriend, self.batch)
                self.session.commit()
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.session.close()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

if __name__ == "__main__":

    print("-------------------------")
    if DESTRUCTIVE_PG:
        print("DROPPING USER FRIENDS TABLE...")
        UserFriend.__table__.drop(db)

    if not UserFriend.__table__.exists():
        print("MIGRATING USER FRIENDS TABLE...")
        UserFriend.__table__.create(db)

    #pipeline = Pipeline()
    #pipeline.perform()
    #pipeline.report()
    #exit()

    print("-------------------------")
    print("PG PIPELINE...")
    print("  BATCH SIZE:", BATCH_SIZE)
    print("  DESTRUCTIVE MIGRATIONS:", DESTRUCTIVE_PG)

    bq = BigQueryService.cautiously_initialized()

    # PERFORM
    session = BoundSession()
    print("  SESSION:", type(session))

    print(generate_timestamp())
    start_at = time.perf_counter()
    counter = 0
    batch = []
    for row in bq.fetch_user_friends_in_batches():
        counter+=1
        #print(counter, row["user_id"], row["screen_name"]) # doesn't print until the very end?
        #session.add(UserFriend(
        #    user_id=row["user_id"],
        #    screen_name=row["screen_name"],
        #    friend_count=row["friend_count"],
        #    friend_names=row["friend_names"]
        #))
        #session.commit()

        batch.append({
            "user_id": row["user_id"],
            "screen_name": row["screen_name"],
            "friend_count": row["friend_count"],
            "friend_names": row["friend_names"]
        })
        if len(batch) >= BATCH_SIZE:
            print(generate_timestamp(), "SAVING BATCH OF", len(batch)) # prints in real-time, just takes a while to get from script invocation to the first batch...
            session.bulk_insert_mappings(UserFriend, batch)
            session.commit()
            batch = []

    end_at = time.perf_counter()
    print(generate_timestamp())
    session.close()

    # REPORT
    duration_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {counter} USERS IN {duration_seconds} SECONDS")
