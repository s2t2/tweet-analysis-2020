
import os
import json

from tweepy.error import TweepError
from pandas import DataFrame
from dotenv import load_dotenv

from app import DATA_DIR, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default=100)) # the max number of processed users to store in BQ at once (with a single insert API call). must be less than 10,000 to avoid error.

if __name__ == "__main__":

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    rows = list(bq_service.fetch_idless_screen_names())
    row_count = len(rows)
    print("-------------------------")
    print(f"FETCHED {row_count} SCREEN NAMES")
    print("BATCH SIZE:", BATCH_SIZE)
    print("-------------------------")

    seek_confirmation()
    bq_service.migrate_user_id_lookups()

    batch = []
    for index, row in enumerate(rows):
        counter = index + 1

        try:
            user_id = twitter_service.get_user_id(row.screen_name)
            message = None
        except TweepError as err:
            #print(err)
            #> [{'code': 50, 'message': 'User not found.'}]
            #> [{'code': 63, 'message': 'User has been suspended.'}]
            user_id = None
            message = json.loads(err.reason.replace("'", '"'))[0]["message"]

        lookup = {"lookup_at": logstamp(), "counter": counter, "screen_name": row.screen_name.upper(), "user_id": user_id, "message": message}
        print(lookup)
        batch.append(lookup)

        if (len(batch) >= BATCH_SIZE) or (counter >= row_count): # if the batch is full or the row is last
            print("SAVING BATCH...")
            bq_service.upload_user_id_lookups(batch)
            batch = [] # clear the batch

    print("-------------")
    print("LOOKUPS COMPLETE!")

    #print("WRITING TO CSV...")
    #df = DataFrame(lookups)
    #print(df.head())
    #csv_filepath = os.path.join(DATA_DIR, "user_id_lookups.csv")
    #df.to_csv(csv_filepath, index=False)

    # google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/tweet-collector-py/datasets/impeachment_production/tables/user_id_lookups/insertAll: too many rows present in the request, limit: 10000 row count: 17196.
    #bq_service.upload_user_id_lookups(lookups[0:9000])
    #bq_service.upload_user_id_lookups(lookups[9000:18000])
    # moving forward need to insert in batches less than 10000
