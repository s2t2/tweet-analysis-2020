
import time
import os
from dotenv import load_dotenv

from app import APP_ENV
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService
from app.models import BoundSession, db, UserFriend, UserDetail, RetweeterDetail

load_dotenv()

USERS_LIMIT = os.getenv("USERS_LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100))
PG_DESTRUCTIVE = (os.getenv("PG_DESTRUCTIVE", default="false") == "true")

def clean_string(dirty):
    """
    Cleans a string so it can be stored in PG without raising an error.

    Param: dirty (string or None) the string to be cleaned.
    """
    if dirty:
        clean = dirty.replace("\x00", "\uFFFD") # fixes "ValueError: A string literal cannot contain NUL (0x00) characters."
    else:
        clean = None
    return clean

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

        if self.pg_destructive and UserFriend.__table__.exists():
            print("DROPPING THE USER FRIENDS TABLE!")
            UserFriend.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not UserFriend.__table__.exists():
            print("CREATING THE USER FRIENDS TABLE!")
            UserFriend.__table__.create(self.pg_engine)
            self.pg_session.commit()

        print(logstamp(), "DATA FLOWING...")
        for row in self.bq_service.fetch_user_friends_in_batches(limit=self.users_limit):
            self.batch.append({
                "user_id": row["user_id"],
                "screen_name": row["screen_name"],
                "friend_count": row["friend_count"],
                "friend_names": row["friend_names"]
            })
            self.counter+=1

            if len(self.batch) >= self.batch_size:
                print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
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

        if self.pg_destructive and UserDetail.__table__.exists():
            print("DROPPING THE USER DETAILS TABLE!")
            UserDetail.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not UserDetail.__table__.exists():
            print("CREATING THE USER DETAILS TABLE!")
            UserDetail.__table__.create(self.pg_engine)
            self.pg_session.commit()

        print(logstamp(), "DATA FLOWING LIKE WATER...")
        for row in self.bq_service.fetch_user_details_in_batches(limit=self.users_limit):
            item = {
                "user_id": row['user_id'],

                "screen_name": clean_string(row['screen_name']),
                "name": clean_string(row['name']),
                "description": clean_string(row['description']),
                "location": clean_string(row['location']),
                "verified": row['verified'],
                "created_at": row['created_at'], #.strftime("%Y-%m-%d %H:%M:%S"),

                "screen_name_count": row['screen_name_count'],
                "name_count": row['name_count'],
                "description_count": row['description_count'],
                "location_count": row['location_count'],
                "verified_count": row['verified_count'],
                "created_count": row['created_at_count'],

                "screen_names": [clean_string(s) for s in row['screen_names']],
                "names": [clean_string(s) for s in row['names']],
                "descriptions": [clean_string(s) for s in row['descriptions']],
                "locations": [clean_string(s) for s in row['locations']],
                "verifieds": row['verifieds'],
                "created_ats": row['created_ats'], #[dt.strftime("%Y-%m-%d %H:%M:%S") for dt in row['_created_ats']]

                "friend_count":        row["friend_count"],

                "status_count":        row["status_count"],
                "retweet_count":       row["retweet_count"],

                # # todo: these topics are specific to the impeachment dataset, so will need to generalize if/when working with another topic (leave for future concern)
                # "impeach_and_convict": row["impeach_and_convict"],
                # "senate_hearing":      row["senate_hearing"],
                # "ig_hearing":          row["ig_hearing"],
                # "facts_matter":        row["facts_matter"],
                # "sham_trial":          row["sham_trial"],
                # "maga":                row["maga"],
                # "acquitted_forever":   row["acquitted_forever"],

            }
            self.batch.append(item)
            self.counter+=1

            # temporarily testing individual inserts...
            #record = UserDetail(**item)
            #self.pg_session.add(record)
            #self.pg_session.commit()

            if len(self.batch) >= self.batch_size:
                print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(UserDetail, self.batch)
                self.pg_session.commit()
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.pg_session.close()

    def download_retweeter_details(self):
        self.start_at = time.perf_counter()
        self.batch = []
        self.counter = 0

        if self.pg_destructive and RetweeterDetail.__table__.exists():
            print("DROPPING THE RETWEETER DETAILS TABLE!")
            RetweeterDetail.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not RetweeterDetail.__table__.exists():
            print("CREATING THE RETWEETER DETAILS TABLE!")
            RetweeterDetail.__table__.create(self.pg_engine)
            self.pg_session.commit()

        print(logstamp(), "DATA FLOWING LIKE WATER...")
        for row in self.bq_service.fetch_retweeter_details_in_batches(limit=self.users_limit):
            item = {
                "user_id": row['user_id'],

                "verified":            row["verified"],
                "created_at":          row["created_at"],
                "screen_name_count":   row["screen_name_count"],
                "name_count":          row["name_count"],

                "retweet_count":       row["retweet_count"],
                # # todo: these topics are specific to the impeachment dataset, so will need to generalize if/when working with another topic (leave for future concern)
                # "ig_report":           row["ig_report"],
                # "ig_hearing":          row["ig_hearing"],
                # "senate_hearing":      row["senate_hearing"],
                # "not_above_the_law":   row["not_above_the_law"],
                # "impeach_and_convict": row["impeach_and_convict"],
                # "impeach_and_remove":  row["impeach_and_remove"],
                # "facts_matter":        row["facts_matter"],
                # "sham_trial":          row["sham_trial"],
                # "maga":                row["maga"],
                # "acquitted_forever":   row["acquitted_forever"],
                # "country_over_party":  row["country_over_party"],

            }
            self.batch.append(item)
            self.counter+=1

            # temporarily testing individual inserts...
            #record = RetweeterDetail(**item)
            #self.pg_session.add(record)
            #self.pg_session.commit()

            if len(self.batch) >= self.batch_size:
                print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(RetweeterDetail, self.batch)
                self.pg_session.commit()
                self.batch = []

        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.pg_session.close()

    def report(self):
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")

    def sleep(self):
        """
        Delays a job re-start, if running on production,
        for hopefully enough time for someone to shut off the server,
        to prevent the server from doing unnecessary work.
        """
        if APP_ENV == "production":
            print("SLEEPING...")
            time.sleep(12 * 60 * 60) # twelve hours

if __name__ == "__main__":

    pipeline = Pipeline()

    print(dir(pipeline))
