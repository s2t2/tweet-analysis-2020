
import time
import os
from dotenv import load_dotenv

from app import APP_ENV
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService
from app.pg_pipeline.models import BoundSession, db, Tweet, UserFriend, UserDetail, RetweeterDetail, CommunityPrediction #, BotFollower
# todo: inherit start and end from Job class

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
    def __init__(self, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE, pg_destructive=PG_DESTRUCTIVE, bq_service=None):
        self.bq_service = bq_service or BigQueryService()

        if users_limit:
            self.users_limit = int(users_limit)
        else:
            self.users_limit = None
        self.tweets_limit = self.users_limit # todo: combine with users_limit for a more generic rows_limit, since we usually run one script or another, so can reset the var between runs
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


    def start_job(self):
        self.start_at = time.perf_counter()
        self.batch = []
        self.counter = 0

    def end_job(self):
        print("ETL COMPLETE!")
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} ITEMS IN {self.duration_seconds} SECONDS")
        self.pg_session.close()

    def destructively_migrate(self, model_class):
        if self.pg_destructive and model_class.__table__.exists():
            print(f"DROPPING THE {model_class.__table__.name.upper()} TABLE!")
            model_class.__table__.drop(self.pg_engine)
            self.pg_session.commit()

        if not model_class.__table__.exists():
            print(f"CREATING THE {model_class.__table__.name.upper()} TABLE!")
            model_class.__table__.create(self.pg_engine)
            self.pg_session.commit()

    def download_tweets(self, start_at=None, end_at=None):
        self.start_job()
        self.destructively_migrate(Tweet)

        print(logstamp(), "DATA FLOWING...")
        for row in self.bq_service.fetch_tweets_in_batches(limit=self.tweets_limit, start_at=start_at, end_at=end_at):
            status_text = row["status_text"]
            try: status_text = clean_string(status_text[0:500]) # truncate strings over 500
            finally: pass

            self.batch.append({
                "status_id": row["status_id"],
                "status_text": status_text,
                "truncated": row["truncated"],
                "retweeted_status_id ": row["retweeted_status_id"],
                "retweeted_user_id ": row["retweeted_user_id"],
                "retweeted_user_screen_name": row["retweeted_user_screen_name"],
                "reply_status_id": row["reply_status_id"],
                "reply_user_id": row["reply_user_id"],
                "is_quote": row["is_quote"],
                "geo": clean_string(row["geo"]),
                "created_at": row["created_at"],

                "user_id": row["user_id"],
                "user_name": clean_string(row["user_name"]),
                "user_screen_name": clean_string(row["user_screen_name"]),
                "user_description": clean_string(row["user_description"]),
                "user_location": clean_string(row["user_location"]),
                "user_verified": row["user_verified"],
                "user_created_at": row["user_created_at"]
            })
            self.counter+=1

            if len(self.batch) >= self.batch_size:
                print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(Tweet, self.batch)
                self.pg_session.commit()
                self.batch = []

        self.end_job()

    def download_user_friends(self):
        self.start_job()
        self.destructively_migrate(UserFriend)

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

        self.end_job()

    def download_user_details(self):
        self.start_job()
        self.destructively_migrate(UserDetail)

        print(logstamp(), "DATA FLOWING...")
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

                "friend_count": row["friend_count"],
                "status_count": row["status_count"],
                "retweet_count": row["retweet_count"],
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

        self.end_job()

    def download_retweeter_details(self):
        self.start_job()
        self.destructively_migrate(RetweeterDetail)

        print(logstamp(), "DATA FLOWING...")
        for row in self.bq_service.fetch_retweeter_details_in_batches(limit=self.users_limit):
            item = {
                "user_id": row['user_id'],

                "verified":            row["verified"],
                "created_at":          row["created_at"],
                "screen_name_count":   row["screen_name_count"],
                "name_count":          row["name_count"],

                "retweet_count":       row["retweet_count"],
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

        self.end_job()

    #def download_bot_followers(self, bot_min=0.8):
    #    self.start_job()
    #    self.destructively_migrate(BotFollower)
    #
    #    print(logstamp(), "DATA FLOWING...")
    #    for row in self.bq_service.fetch_bot_followers_in_batches(bot_min=bot_min):
    #        self.batch.append({"bot_id": row["bot_id"], "follower_id": row["follower_id"]})
    #        self.counter+=1
    #
    #        if len(self.batch) >= self.batch_size:
    #            print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
    #            self.pg_session.bulk_insert_mappings(BotFollower, self.batch)
    #            self.pg_session.commit()
    #            self.batch = []
    #
    #    self.end_job()

    def download_community_predictions(self, start_at=None, end_at=None):
        self.start_job()
        self.destructively_migrate(CommunityPrediction)

        print(logstamp(), "DATA FLOWING...")
        for row in self.bq_service.fetch_predictions(limit=self.tweets_limit):
            self.batch.append(dict(row))

            self.counter+=1
            if len(self.batch) >= self.batch_size:
                print(logstamp(), fmt_n(self.counter), "SAVING BATCH...")
                self.pg_session.bulk_insert_mappings(CommunityPrediction, self.batch)
                self.pg_session.commit()
                self.batch = []

        self.end_job()


if __name__ == "__main__":

    pipeline = Pipeline()

    print(dir(pipeline))
