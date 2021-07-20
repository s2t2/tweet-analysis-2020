
import os
from pprint import pprint

from dotenv import load_dotenv
from app.bq_service import BigQueryService, split_into_batches
from app.twitter_service import TwitterService

load_dotenv()

STATUS_LIMIT = int(os.getenv("STATUS_LIMIT", default="100_000")) # number of ids to fetch from BQ
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100")) # must be less than 100


if __name__ == '__main__':


    bq_service = BigQueryService()
    twitter_api = TwitterService().api

    print("LIMIT:", STATUS_LIMIT)
    print("BATCH SIZE:", BATCH_SIZE)

    # FETCH STATUS IDS

    sql = f"""
        SELECT DISTINCT ids.status_id
        FROM `{bq_service.dataset_address}.all_status_ids` ids
        LEFT JOIN `{bq_service.dataset_address}.all_status_id_lookups` lookups ON lookups.status_id = ids.status_id
        WHERE lookups.status_id IS NULL
        LIMIT {STATUS_LIMIT}
    """
    results = list(bq_service.execute_query(sql))
    print("FETCHED STATUS IDS:", len(results))

    for batch in split_into_batches(results, batch_size=BATCH_SIZE):
        print("PROCESSING BATCH...")
        print(batch)
        status_ids = [row["status_id"] for row in batch]
        # FETCH FULL STATUS INFO
        # including urls
        # and full text
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
            print("---------")
