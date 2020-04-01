from datetime import datetime
import os
from dotenv import load_dotenv
from google.cloud import bigquery

from app import APP_ENV

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_development") #> "_test" or "_production"
DESTRUCTIVE_MIGRATIONS = (os.getenv("DESTRUCTIVE_MIGRATIONS", default="false") == "true")
VERBOSE_QUERIES = (os.getenv("VERBOSE_QUERIES", default="false") == "true")

class BigQueryService():

    def __init__(self, project_name=PROJECT_NAME, dataset_name=DATASET_NAME, init_tables=False,
                        verbose=VERBOSE_QUERIES, destructive=DESTRUCTIVE_MIGRATIONS):
        self.project_name = project_name
        self.dataset_name = dataset_name
        self.dataset_address = f"{self.project_name}.{self.dataset_name}"

        self.verbose = (verbose == True)
        self.destructive = (destructive == True)

        self.client = bigquery.Client()
        self.dataset_ref = self.client.dataset(self.dataset_name)
        if init_tables == True:
            self.init_tables()

    def init_tables(self):
        """ Creates new tables for storing follower graphs """
        self.migrate_populate_users()
        self.migrate_user_friends()
        user_friends_table_ref = self.dataset_ref.table("user_friends")
        self.user_friends_table = self.client.get_table(user_friends_table_ref) # an API call (caches results for subsequent inserts)

    def execute_query(self, sql):
        """Param: sql (str)"""
        if self.verbose:
            print(sql)
        job = self.client.query(sql)
        return job.result()

    def migrate_populate_users(self):
        """
        Resulting table has a row for each user id / screen name combo
            (multiple rows per user id if they changed their screen name)
        """
        sql = ""
        if self.destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.users`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.users` as (
                SELECT
                    user_id
                    ,user_screen_name as screen_name
                    ,max(user_verified) as verified
                FROM `{self.dataset_address}.tweets`
                WHERE user_id IS NOT NULL AND user_screen_name IS NOT NULL
                GROUP BY 1, 2
                ORDER BY 1
            );
        """
        results = self.execute_query(sql)
        return list(results)

    def migrate_user_friends(self):
        sql = ""
        if self.destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.user_friends`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.user_friends` (
                user_id STRING,
                screen_name STRING,
                verified BOOLEAN,
                friend_count INT64,
                friend_names ARRAY<STRING>,
                start_at TIMESTAMP,
                end_at TIMESTAMP
            );
        """
        results = self.execute_query(sql)
        return list(results)

    def fetch_remaining_users(self, min_id=None, max_id=None, limit=None):
        """Returns a list of table rows"""
        sql = f"""
            SELECT
                u.user_id
                ,u.screen_name
                ,u.verified
            FROM `{self.dataset_address}.users` u
            LEFT JOIN `{self.dataset_address}.user_friends` f ON u.user_id = f.user_id
            WHERE f.user_id IS NULL
        """
        if min_id and max_id:
            sql += f"  AND CAST(u.user_id as int64) BETWEEN {int(min_id)} AND {int(max_id)} "
            sql += f"ORDER BY u.user_id;"
        elif limit:
            sql += f"ORDER BY u.user_id "
            sql += f"LIMIT {limit};"
        else:
            sql += f"ORDER BY u.user_id;"
        results = self.execute_query(sql)
        return list(results)

    def append_user_friends(self, records):
        """
        Param: records (list of dictionaries)
        """
        rows_to_insert = [list(d.values()) for d in records]
        #rows_to_insert = [list(d.values()) for d in records if any(d["friend_names"])] # doesn't store failed attempts. can try those again later
        #if any(rows_to_insert):
        errors = self.client.insert_rows(self.user_friends_table, rows_to_insert)
        return errors

if __name__ == "__main__":

    service = BigQueryService()
    print("BIGQUERY DATASET:", service.dataset_address.upper())
    print("DESTRUCTIVE MIGRATIONS:", service.destructive)
    print("VERBOSE QUERIES:", service.verbose)
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()

    #print("--------------------")
    #print("FETCHING TOPICS...")
    #sql = f"""
    #    SELECT topic, created_at
    #    FROM `{self.dataset_address}.topics`
    #    ORDER BY created_at;
    #"""
    #results = service.execute_query(sql)
    #for row in results:
    #    print(row)
    #    print("---")

    print("--------------------")
    #print("COUNTING TWEETS AND USERS...")
    sql = f"""
        SELECT
            count(distinct status_id) as tweet_count
            ,count(distinct user_id) as user_count
        FROM `{service.dataset_address}.tweets`
    """
    results = service.execute_query(sql)
    first_row = list(results)[0]
    user_count = first_row.user_count
    print(f"TWEETS: {first_row.tweet_count:,}") # formatting with comma separators for large numbers
    print(f"USERS: {user_count:,}") # formatting with comma separators for large numbers

    #print("--------------------")
    #print("FETCHING LATEST TWEETS...")
    #sql = f"""
    #    SELECT
    #        status_id, status_text, geo, created_at,
    #        user_id, user_screen_name, user_description, user_location, user_verified
    #    FROM `{service.dataset_address}.tweets`
    #    ORDER BY created_at DESC
    #    LIMIT 3
    #"""
    #results = service.execute_query(sql)
    #for row in results:
    #    print(row)
    #    print("---")

    service.init_tables()

    print("--------------------")
    #print("COUNTING USER FRIEND GRAPHS...")
    sql = f"""
        SELECT count(distinct user_id) as user_count
        FROM `{service.dataset_address}.user_friends`
    """
    results = service.execute_query(sql)
    graphed_user_count = list(results)[0].user_count
    print("USERS WITH FRIEND GRAPHS:", graphed_user_count)
    percent_collected = graphed_user_count / user_count
    print(f"{(percent_collected * 100):.1f}% COLLECTED")
    print(f"{((1 - percent_collected) * 100):.1f}% REMAINING")

    print("--------------------")
    print("FETCHING LATEST FRIEND GRAPHS...")
    sql = f"""
        SELECT
            user_id
            ,screen_name
            ,verified
            ,friend_count
            ,friend_names
            ,start_at
            ,end_at
        FROM `{service.dataset_address}.user_friends`
        ORDER BY start_at DESC
        LIMIT 3
    """
    results = service.execute_query(sql)
    for row in results:
        print("---")
        print(row.screen_name, row.friend_count, len(row.friend_names))
