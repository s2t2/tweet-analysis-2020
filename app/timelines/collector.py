

# source: https://github.com/s2t2/tweet-analysis-2021/blob/main/app/tweet_parser.py

import os
from time import sleep
from functools import lru_cache
from dotenv import load_dotenv
#from tqdm import tqdm as progress_bar

from app import seek_confirmation
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import TwitterService
from app.timelines.status_parser import parse_timeline_status

load_dotenv()

USER_LIMIT = os.getenv("USER_LIMIT", default="250")
STATUS_LIMIT = os.getenv("STATUS_LIMIT", default="10_000")

class TimelineCollector():
    def __init__(self, bq_service=None, twitter_service=None, user_limit=USER_LIMIT, status_limit=STATUS_LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.twitter_service = twitter_service or TwitterService()

        self.user_limit = int(user_limit)
        self.status_limit = int(status_limit)

        self.dataset_address = self.bq_service.dataset_address
        #self.parse_status = parse_timeline_status

        print("---------------------------")
        print("JOB: TIMELINE LOOKUPS")
        print("DATASET:", self.dataset_address.upper())
        print("USER LIMIT:", self.user_limit)
        print("STATUS LIMIT:", self.status_limit)
        print("---------------------------")

    #def fetch_users(self):
    #    sql = f"""
    #        WITH user_lookups as (
    #            SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
    #            FROM `{self.dataset_address}.user_lookups`
    #        )
    #
    #        SELECT DISTINCT ul.user_id
    #        FROM user_lookups ul
    #        LEFT JOIN `{self.dataset_address}.timeline_lookups` tl ON tl.user_id = ul.user_id
    #        WHERE ul.error_code IS NULL
    #            AND ul.status_count > 0
    #            AND tl.user_id IS NULL
    #        LIMIT {self.user_limit};
    #    """
    #    #print(sql)
    #    return [row["user_id"] for row in list(self.bq_service.execute_query(sql))]

    @property
    @lru_cache(maxsize=None)
    def lookups_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_lookups") # API call

    @property
    @lru_cache(maxsize=None)
    def timelines_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_tweets") # API call

    def fetch_timeline(self, user_id):
        return self.twitter_service.get_user_timeline(request_params={"user_id": user_id}, limit=self.status_limit)

    def save_timeline(self, timeline):
        return self.bq_service.insert_records_in_batches(records=timeline, table=self.timelines_table)

    def save_lookups(self, lookups):
        return self.bq_service.insert_records_in_batches(records=lookups, table=self.lookups_table)


if __name__ == '__main__':
    from pprint import pprint

    job = TimelineCollector()

    seek_confirmation()

    #
    # GET USERS, EXCLUDING THOSE WHO ARE: SUSPENDED, NOT FOUND, PREVIOUSLY LOOKED-UP
    #

    user_ids = job.fetch_users()
    print("USERS:", len(user_ids))
    if not any(user_ids):
        print("SLEEPING...")
        sleep(10 * 60 * 60) # let the server rest while we have time to shut it down
        exit() # don't try to do more work

    lookups = []
    try:

        #
        # GET TIMELINE TWEETS FOR EACH USER
        #

        for index, user_id in enumerate(user_ids):
            print("---------------------")
            print("USER ID:", index, user_id)

            lookup = {
                "user_id": user_id,
                "timeline_length": None,
                "error_type": None,
                "error_message": None,
                "start_at": generate_timestamp(),
                "end_at": None
            }
            timeline = []

            try:
                for status in job.fetch_statuses(user_id=user_id):
                    timeline.append(parse_timeline_status(status))

                lookup["timeline_length"] = len(timeline)
            except Exception as err:
                lookup["error_type"] = err.__class__.__name__
                lookup["error_message"] = str(err)
            lookup["end_at"] = generate_timestamp()
            print(lookup)
            lookups.append(lookup)

            if any(timeline):
                print("SAVING", len(timeline), "TIMELINE TWEETS...")
                errors = job.save_timeline(timeline)
                if errors:
                    pprint(errors)
                    #breakpoint()

    finally:
        # ensure there aren't any situations where
        # ... the timeline gets saved above, but the lookup record does not get saved below
        # ... (like in the case of an unexpected error or something)
        if any(lookups):
            print("SAVING", len(lookups), "LOOKUPS...")
            errors = job.save_lookups(lookups)
            if errors:
                pprint(errors)
                #breakpoint()

    print("JOB COMPLETE!")
