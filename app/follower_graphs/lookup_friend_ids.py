
import os
import json

from tweepy.error import TweepError
from pandas import DataFrame

from app import DATA_DIR, seek_confirmation
from app.job import Job
from app.decorators.datetime_decorators import logstamp
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=1000)) # the max number of processed users to store in BQ at once (with a single insert API call). must be less than 10,000 to avoid error.

class LookupFriendIds(Job):
    def __init__(self):
        self.bq_service = BigQueryService()
        self.twitter_service = TwitterService()

        print("-------------------------")
        print("LOOKUP FRIEND IDS...")
        print("  LIMIT:", LIMIT)
        print("  BATCH SIZE:", BATCH_SIZE)

        Job.__init__(self)

        seek_confirmation()
        #self.bq_service.migrate_friend_id_lookups_table()

    def perform(self):
        self.batch = []
        self.start()

        for row in self.bq_service.fetch_idless_friend_names_in_batches(limit=LIMIT):
            self.counter += 1
            self.batch.append(self.perform_lookup(row.user_screen_name))

            if len(self.batch) >= BATCH_SIZE: # full batches
                print("SAVING BATCH...", len(self.batch))
                self.bq_service.upload_friend_id_lookups(self.batch)
                self.batch = [] # clear the batch

        if len(batch) >= 0: # last batch
            print("SAVING BATCH...", len(self.batch))
            self.bq_service.upload_friend_id_lookups(self.batch)
            self.batch = [] # clear the batch

        self.end()
        print("-------------")
        print("LOOKUPS COMPLETE!")

    def perform_lookup(self, screen_name):
        try:
            user_id = self.twitter_service.get_user_id(screen_name)
            message = None
        except TweepError as err:
            #print(err)
            #> [{'code': 50, 'message': 'User not found.'}]
            #> [{'code': 63, 'message': 'User has been suspended.'}]
            user_id = None
            message = json.loads(err.reason.replace("'", '"'))[0]["message"]
        lookup = {
            "lookup_at": logstamp(),
            "counter": self.counter,
            "screen_name": screen_name.upper(),
            "user_id": user_id,
            "message": message
        }
        return lookup


if __name__ == "__main__":


    job = LookupFriendIds()

    job.perform()
