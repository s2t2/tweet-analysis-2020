
import time
import os
from dotenv import load_dotenv

from app.models import db, UserFriend, BoundSession
from app.storage_service import BigQueryService, generate_timestamp, bigquery

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=10)) # use 1,000 or 10,000 in production
DESTRUCTIVE_MIGRATIONS = (os.getenv("DESTRUCTIVE_MIGRATIONS", default="false") == "true")

class Pipeline():
    def __init__(self, batch_size=BATCH_SIZE, bq=None):
        self.bq = (bq or BigQueryService.cautiously_initialized())
        self.db = db
        self.session = BoundSession()
        self.batch_size = batch_size
        self.batch = []
        self.counter = 0

    def perform(self):
        self.start_at = time.perf_counter()

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

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

if __name__ == "__main__":

    if DESTRUCTIVE_MIGRATIONS:
        print("DROPPING USER FRIENDS TABLE...")
        UserFriend.__table__.drop(db)

    if not UserFriend.__table__.exists():
        print("MIGRATING USER FRIENDS TABLE...")
        UserFriend.__table__.create(db)

    pipeline = Pipeline()
    pipeline.perform()
    pipeline.report()
    pipeline.session.close()
