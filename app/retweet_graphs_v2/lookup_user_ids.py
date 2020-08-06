
import os
import json

from tweepy.error import TweepError
from pandas import DataFrame

from app import DATA_DIR
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService


if __name__ == "__main__":

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    counter = 1
    lookups = []
    for row in bq_service.fetch_idless_screen_names():

        try:
            user_id = twitter_service.get_user_id(row.screen_name)
            message = None
        except TweepError as err:
            #print(err)
            #> [{'code': 50, 'message': 'User not found.'}]
            #> [{'code': 63, 'message': 'User has been suspended.'}]
            user_id = None
            message = json.loads(err.reason.replace("'", '"'))[0]["message"]

        lookup = {"counter": counter, "screen_name": row.screen_name.upper(), "user_id": user_id, "message": message}
        print(lookup)
        lookups.append(lookup)
        counter+=1

    print("-------------")
    print("LOOKUPS COMPLETE!")
    df = DataFrame(lookups)
    print(df.head())
    csv_filepath = os.path.join(DATA_DIR, "user_id_lookups.csv")
    df.to_csv(csv_filepath, index=False)
