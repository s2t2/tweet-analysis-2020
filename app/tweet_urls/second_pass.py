
import os
from pprint import pprint

from dotenv import load_dotenv
from app.bq_service import BigQueryService, split_into_batches
from app.twitter_service import TwitterService

load_dotenv()

BATCH_SIZE = os.getenv("BATCH_SIZE", default="100") # must be less than 100


if __name__ == '__main__':

    bq_service = BigQueryService()
    twitter_api = TwitterService().api

    sql = f"""

    """

    status_ids = bq_service.execute_query(sql)
    for batch in split_into_batches(status_ids, batch_size=BATCH_SIZE):

        # https://docs.tweepy.org/en/stable/api.html#API.statuses_lookup
        # max per request is 100
        full_statuses = twitter_api.statuses_lookup(
            id_=status_ids,
            include_entities=True, # this is where the full urls are
            trim_user=True,
            #map_=True # A boolean indicating whether or not to include tweets that cannot be shown. Defaults to False.
            include_ext_alt_text=True,
            include_card_uri=False
        )

        for status in full_statuses:
            pprint(status._json)
