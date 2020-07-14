
import time
import os
from dotenv import load_dotenv

from app import APP_ENV
from app.workers import USERS_LIMIT, BATCH_SIZE, fmt_ts, fmt_n
from app.bq_service import BigQueryService
from app.models import BoundSession, db, UserFriend, UserDetail

load_dotenv()

PG_DESTRUCTIVE = (os.getenv("PG_DESTRUCTIVE", default="false") == "true")

class Pipeline():
    def __init__(self, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE,
                        pg_destructive=PG_DESTRUCTIVE, bq_service=None):
        self.bq_service = (bq_service or BigQueryService.cautiously_initialized())
        if users_limit:
            self.users_limit = int(users_limit)
        else:
            self.users_limit = None
        self.batch_size = batch_size

        self.pg_destructive = pg_destructive
        self.pg_engine = db
        self.pg_session = BoundSession()

        print("-------------------------")
        print("PG PIPELINE...")
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)
        #print("  BQ SERVICE:", type(self.bq_service))
        #print("  PG SESSION:", type(self.pg_session))
        print("  PG DESTRUCTIVE:", self.pg_destructive)

    def download_user_friends(self):
        self.start_at = time.perf_counter()
        self.batch = []
        self.counter = 0

        if self.pg_destructive:
            print("DROPPING THE USER FRIENDS TABLE!")
            UserFriend.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not UserFriend.__table__.exists():
            print("CREATING THE USER FRIENDS TABLE!")
            UserFriend.__table__.create(self.pg_engine)
            self.pg_session.commit()

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
                print(fmt_ts(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(UserFriend, self.batch)
                self.pg_session.commit()
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.pg_session.close()

    def download_user_details(self):
        self.start_at = time.perf_counter()
        self.batch = []
        self.counter = 0

        if self.pg_destructive:
            print("DROPPING THE USER DETAILS TABLE!")
            UserDetail.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not UserDetail.__table__.exists():
            print("CREATING THE USER DETAILS TABLE!")
            UserDetail.__table__.create(self.pg_engine)
            self.pg_session.commit()

        print(fmt_ts(), "DATA FLOWING LIKE WATER...")
        for row in self.bq_service.fetch_user_details_in_batches(limit=self.users_limit):
            item = {
                "user_id": row['user_id'],

                "screen_name": row['screen_name'],
                "name": row['name'],
                "description": row['description'],
                "location": row['location'],
                "verified": row['verified'],
                "created_at": row['created_at'], #.strftime("%Y-%m-%d %H:%M:%S"),

                "screen_name_count": row['_screen_name_count'],
                "name_count": row['_name_count'],
                "description_count": row['_description_count'],
                "location_count": row['_location_count'],
                "verified_count": row['_verified_count'],
                "created_count": row['_created_at_count'],

                "screen_names": row['_screen_names'],
                "names": row['_names'],
                "descriptions": row['_descriptions'],
                "locations": row['_locations'],
                "verifieds": row['_verifieds'],
                "created_ats": row['_created_ats'] #[dt.strftime("%Y-%m-%d %H:%M:%S") for dt in row['_created_ats']]
            }
            self.batch.append(item)
            self.counter+=1

            # temporarily testing individual inserts...
            #record = UserDetail(**item)
            #self.pg_session.add(record)
            #self.pg_session.commit()

            if len(self.batch) >= self.batch_size:
                print(fmt_ts(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(UserDetail, self.batch)
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
    pipeline.download_user_friends()
    pipeline.report()

    if APP_ENV == "production":
        print("SLEEPING...")
        time.sleep(12 * 60 * 60) # twelve hours
