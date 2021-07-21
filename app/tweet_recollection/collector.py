
import os
from pprint import pprint

from dotenv import load_dotenv

from app import seek_confirmation
from app.bq_service import BigQueryService, split_into_batches, generate_timestamp
from app.twitter_service import TwitterService

from app.tweet_recollection.parser import parse_full_text

load_dotenv()

STATUS_LIMIT = int(os.getenv("STATUS_LIMIT", default="100_000")) # number of ids to fetch from BQ
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100")) # must be less than 100

class Collector:
    def __init__(self):
        self.twitter_api = TwitterService().api
        self.bq_service = BigQueryService()
        self.limit = STATUS_LIMIT
        self.batch_size = BATCH_SIZE

    def fetch_remaining_status_ids(self):
        sql = f"""
            SELECT DISTINCT ids.status_id
            FROM `{self.bq_service.dataset_address}.all_status_ids` ids
            LEFT JOIN `{self.bq_service.dataset_address}.all_status_id_lookups` lookups ON lookups.status_id = ids.status_id
            WHERE lookups.status_id IS NULL
            LIMIT {self.limit}
        """
        return [row["status_id"] for row in list(self.bq_service.execute_query(sql))]

    def perform(self):
        for batch_of_ids in split_into_batches(self.fetch_remaining_status_ids(), batch_size=self.batch_size):
            print("PROCESSING BATCH...", generate_timestamp())
            self.process_batch(batch_of_ids)

    def lookup_statuses(self, status_ids):
        """Fetch full status info including urls, and full text.
            Max per request is 100, so batch size must be smaller than that.
            See:
                https://docs.tweepy.org/en/stable/api.html#API.statuses_lookup
                https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.twitter_api.statuses_lookup(
            id_=status_ids,
            include_entities=True, # this is where the full urls are
            trim_user=True, # we already have this info
            include_ext_alt_text=True, # If alt text has been added to any attached media entities, this parameter will return an ext_alt_text value in the top-level key for the media entity. If no value has been set, this will be returned as null.
            include_card_uri=False,
            map_=True, # "Tweets that do not exist or cannot be viewed by the current user will still have their key represented but with an explicitly null value paired with it"

            tweet_mode="extended"
        )

    def process_batch(self, status_ids):
        recollected_statuses = []
        recollected_urls = []
        for status in self.lookup_statuses(status_ids):
            try:

                pprint(status._json)

                status_id = status.id_str

                recollected_statuses.append({
                    "status_id": status_id,
                    "full_text": parse_full_text(status)
                })

                for url in status.entities["urls"]:
                    recollected_urls.append({
                        "status_id": status.id_str,
                        "expanded_url": url.get("expanded_url"),
                        "unwound_url": url.get("unwound").get("url"),
                        "unwound_title": url.get("unwound").get("title"),
                        "unwound_description": url.get("unwound").get("description"),
                    })

            except Exception as err:
                print('OOPS', err)
                breakpoint()


            # TODO: save batch to BQ



if __name__ == '__main__':

    collector = Collector()

    print("LIMIT:", collector.limit)
    print("BATCH SIZE:", collector.batch_size)

    seek_confirmation()

    collector.perform()
