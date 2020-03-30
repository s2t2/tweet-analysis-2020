from datetime import datetime
import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_development") #> "_test" or "_production"

class BigQueryService():

    def __init__(self, project_name=PROJECT_NAME, dataset_name=DATASET_NAME):
        self.project_name = project_name
        self.dataset_name = dataset_name #> "impeachment_production", "impeachment_test", etc.
        self.client = bigquery.Client()
        self.dataset_ref = self.client.dataset(self.dataset_name)
        self.dataset_address = f"{self.project_name}.{self.dataset_name}"
        #self.tweets_table_ref = self.dataset_ref.table("tweets")
        #self.tweets_table = self.client.get_table(self.tweets_table_ref) # an API call (caches results for subsequent inserts)
        #self.topics_table_ref = self.dataset_ref.table("topics")
        #self.topics_table = self.client.get_table(self.topics_table_ref) # an API call (caches results for subsequent inserts)

    def execute_query(self, sql):
        """Param: sql (str)"""
        job = self.client.query(sql)
        return job.result()

    def fetch_topics(self):
        sql = f"""
            SELECT topic, created_at
            FROM `{self.dataset_address}.topics`
            ORDER BY created_at;
        """
        results = self.execute_query(sql)
        return list(results)

    def migrate_user_friends(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.dataset_address}.user_friends as (
                SELECT
                    distinct(status_id) as user_id
                    ,NULL as friend_ids
                FROM `{self.dataset_address}.tweets`
                ORDER BY 1
            );
        """
        results = self.execute_query(sql)
        return list(results)

    def fetch_user_friends(self):
        """Returns a list of table rows"""
        sql = f"""
            SELECT user_id, friend_ids
            FROM `{self.dataset_address}.user_friends`
            ORDER BY user_id;
        """
        results = self.execute_query(sql)
        print(type(results))
        print(results)
        return list(results)

if __name__ == "__main__":

        service = BigQueryService()
        print("BIGQUERY DATASET:", service.dataset_address.upper())

        user_friends = service.fetch_user_friends()
        for row in user_friends:
            print("USER:", row.user_id)


        exit()







        print("--------------------")
        print("FETCHING TOPICS...")
        results = service.fetch_topics()
        for row in results:
            print(row)
            print("---")

        print("--------------------")
        print("COUNTING TWEETS...")
        sql = f"SELECT count(distinct status_id) as tweets_count FROM `{service.dataset_address}.tweets`"
        results = service.execute_query(sql)
        print(list(results)[0].tweets_count)

        print("--------------------")
        print("FETCHING LATEST TWEETS...")
        sql = f"""
            SELECT
                status_id, status_text, geo, created_at,
                user_id, user_screen_name, user_description, user_location, user_verified
            FROM `{service.dataset_address}.tweets`
            ORDER BY created_at DESC
            LIMIT 3
        """
        results = service.execute_query(sql)
        for row in results:
            print(row)
            print("---")




        exit()

        #results = service.migrate_user_friends()
        #print(results)
