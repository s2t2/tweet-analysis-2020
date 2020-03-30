from datetime import datetime
import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_production") #> "impeachment_production"

class BigQueryService():
    def __init__(self, project_name=PROJECT_NAME, dataset_name=DATASET_NAME):
        self.project_name = project_name
        self.dataset_name = dataset_name #> "impeachment_production", "impeachment_test", etc.

        self.client = bigquery.Client()

        self.dataset_ref = self.client.dataset(self.dataset_name)
        self.dataset_address = f"{self.project_name}.{self.dataset_name}"
        print("BIGQUERY DATASET:", self.dataset_address.upper())

        self.tweets_table_name = "tweets"
        self.tweets_table_ref = self.dataset_ref.table(self.tweets_table_name)
        self.tweets_table = self.client.get_table(self.tweets_table_ref) # an API call (caches results for subsequent inserts)
        self.tweets_table_address = f"{self.dataset_address}.{self.tweets_table_name}"

        self.topics_table_name = "topics"
        self.topics_table_ref = self.dataset_ref.table(self.topics_table_name)
        self.topics_table = self.client.get_table(self.topics_table_ref) # an API call (caches results for subsequent inserts)
        self.topics_table_address = f"{self.dataset_address}.{self.topics_table_name}"

    def execute_query(self, sql):
        """Param: sql (str)"""
        job = self.client.query(sql)
        return job.result()

    def fetch_topics(self):
        """Returns a list of table rows"""
        sql = f"""
            SELECT topic, created_at
            FROM `{self.topics_table_address}`
            ORDER BY created_at;
        """
        results = self.execute_query(sql)
        return list(results)




if __name__ == "__main__":

        bq_service = BigQueryService()

        print("--------------------")
        print("FETCHING TOPICS...")
        results = bq_service.fetch_topics()
        for row in results:
            print(row)
            print("---")

        print("--------------------")
        print("COUNTING TWEETS...")
        sql = f"SELECT count(distinct status_id) as tweets_count FROM `{bq_service.tweets_table_address}`"
        results = bq_service.execute_query(sql)
        print(list(results)[0].tweets_count)

        exit()

        print("--------------------")
        print("FETCHING LATEST TWEETS...")
        sql = f"""
            SELECT
                status_id, status_text, geo, created_at,
                user_id, user_screen_name, user_description, user_location, user_verified
            FROM `{bq_service.tweets_table_address}`
            ORDER BY created_at DESC
            LIMIT 3
        """
        results = bq_service.execute_query(sql)
        for row in results:
            print(row)
            print("---")
