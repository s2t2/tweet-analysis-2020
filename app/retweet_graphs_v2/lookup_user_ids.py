
import json
from tweepy.error import TweepError

from app.bq_service import BigQueryService
from app.twitter_service import TwitterService


if __name__ == "__main__":

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    batch = []
    for row in bq_service.fetch_idless_screen_names():

        try:
            #print(row.screen_name)
            user_id = twitter_service.get_user_id(row.screen_name)
            message = None
        except TweepError as err:
            #print(err)
            #> [{'code': 50, 'message': 'User not found.'}]
            #> [{'code': 63, 'message': 'User has been suspended.'}]
            #print("USER SUSPENDED!")
            user_id = None
            message = json.loads(err.reason.replace("'", '"'))[0]["message"]

        lookup = {"screen_name": row.screen_name.upper(), "user_id": user_id, "message": message}
        print(lookup)
        batch.append(lookup)

    breakpoint()
