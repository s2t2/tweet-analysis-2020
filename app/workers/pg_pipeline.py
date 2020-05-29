
import time
import os
from dotenv import load_dotenv

from app.models import UserFriend, BoundSession, db
from app.bq_service import BigQueryService
from app.workers import APP_ENV, USERS_LIMIT, fmt_ts

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))

class Pipeline():
    def __init__(self, batch_size=BATCH_SIZE, users_limit=USERS_LIMIT, bq_service=None):
        self.batch_size = batch_size
        if users_limit:
            self.users_limit = int(users_limit)
        else:
            self.users_limit = None

        self.bq_service = (bq_service or BigQueryService.cautiously_initialized())
        self.pg_session = BoundSession()

        print("-------------------------")
        print("PG PIPELINE...")
        print("  BATCH SIZE:", self.batch_size)
        print("  USERS LIMIT:", self.users_limit)
        print("  BQ SERVICE:", type(self.bq_service))
        print("  PG SESSION:", type(self.pg_session))

    def perform(self):
        self.start_at = time.perf_counter()
        self.batch = []
        self.counter = 0

        print(fmt_ts(), "DATA FLOWING...")
        for row in self.bq_service.fetch_user_friends_in_batches(limit=self.users_limit):
            self.batch.append({
                "user_id": row["user_id"],
                "screen_name": row["screen_name"],
                "friend_count": row["friend_count"],
                "friend_names": row["friend_names"]
            })
            self.counter+=1

            if len(self.batch) >= self.batch_size:
                print(fmt_ts(), "SAVING BATCH OF", len(self.batch))
                self.pg_session.bulk_insert_mappings(UserFriend, self.batch)
                self.pg_session.commit()
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.pg_session.close()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

if __name__ == "__main__":

    pipeline = Pipeline()
    pipeline.perform()
    pipeline.report()

    if APP_ENV == "production":
        print("SLEEPING...")
        time.sleep(12 * 60 * 60) # twelve hours
