from datetime import datetime
import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_development") #> "_test" or "_production"

class BigQueryService():
    """
    See:
        https://cloud.google.com/bigquery/docs/reference/standard-sql/operators
        https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules

    """

    def __init__(self, project_name=PROJECT_NAME, dataset_name=DATASET_NAME):
        self.project_name = project_name
        self.dataset_name = dataset_name
        self.dataset_address = f"{self.project_name}.{self.dataset_name}"

        self.client = bigquery.Client()
        self.dataset_ref = self.client.dataset(self.dataset_name)
        #self.tweets_table_ref = self.dataset_ref.table("tweets")
        #self.tweets_table = self.client.get_table(self.tweets_table_ref) # an API call (caches results for subsequent inserts)
        #self.topics_table_ref = self.dataset_ref.table("topics")
        #self.topics_table = self.client.get_table(self.topics_table_ref) # an API call (caches results for subsequent inserts)
        user_friends_table_ref = self.dataset_ref.table("user_friends_temp")
        self.user_friends_table = self.client.get_table(user_friends_table_ref) # an API call (caches results for subsequent inserts)

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

    def migrate_users(self):
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.dataset_address}.users as (
                SELECT distinct(user_id) as user_id
                FROM `{self.dataset_address}.tweets`
                ORDER BY 1
            );
        """
        results = self.execute_query(sql)
        return list(results)

    def fetch_users(self):
        """Returns a list of table rows"""
        sql = f"""
            SELECT user_id
            FROM `{self.dataset_address}.users`;
        """
        results = self.execute_query(sql)
        return list(results)

    #def fetch_friendless_users(self, min_id=None, max_id=None, limit=None):
    #    """Returns a list of table rows"""
    #
    #    sql = f"""
    #        SELECT user_id
    #        FROM `{self.dataset_address}.user_friends`
    #        WHERE friend_ids IS NULL
    #    """
    #
    #    if min_id is not None and max_id is not None:
    #        sql += "  AND CAST(user_id as int64) BETWEEN {min_id} AND {max_id}"
    #
    #    if limit is not None:
    #        sql += f"LIMIT {limit}"
    #
    #    results = self.execute_query(sql)
    #    return list(results)

    #def update_user_friends(self, user_id, friend_ids):
    #    table_ref = self.dataset_ref.table("topics")
    #    table = self.client.get_table(table_ref) # an API call (caches results for subsequent inserts)
    #
    #    sql = """
    #        UPDATE Customers
    #        SET ContactName = 'Alfred Schmidt', City= 'Frankfurt'
    #        WHERE CustomerID = 1;
    #    """
    #
    #    # TODO

    def migrate_user_friends(self):
        # see: https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#array-type
        sql = f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.user_friends_temp` (
                user_id STRING,
                friends_count INT64,
                friend_ids ARRAY<STRING>
            );
        """
        results = self.execute_query(sql)
        return list(results)

    def append_user_friends(self, records):
        """Param: records (list of dictionaries)"""
        rows_to_insert = [list(d.values()) for d in records]
        errors = self.client.insert_rows(self.user_friends_table, rows_to_insert)
        return errors


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
