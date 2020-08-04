from datetime import datetime
import os
from dotenv import load_dotenv
from google.cloud import bigquery

from app import APP_ENV, seek_confirmation
from app.decorators.number_decorators import fmt_n

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_development") #> "_test" or "_production"
DESTRUCTIVE_MIGRATIONS = (os.getenv("DESTRUCTIVE_MIGRATIONS", default="false") == "true")
VERBOSE_QUERIES = (os.getenv("VERBOSE_QUERIES", default="false") == "true")

DEFAULT_START = "2019-12-02 01:00:00" # the "beginning of time" for the impeachment dataset. todo: allow customization via env var
DEFAULT_END = "2020-03-24 20:00:00" # the "end of time" for the impeachment dataset. todo: allow customization via env var

def generate_timestamp(): # todo: maybe a class method
    """Formats datetime for storing in BigQuery (consider moving)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_temp_table_id(): # todo: maybe a class method
    return datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

class BigQueryService():

    def __init__(self, project_name=PROJECT_NAME, dataset_name=DATASET_NAME, init_tables=False,
                        verbose=VERBOSE_QUERIES, destructive=DESTRUCTIVE_MIGRATIONS):
        self.project_name = project_name
        self.dataset_name = dataset_name
        self.dataset_address = f"{self.project_name}.{self.dataset_name}"

        self.verbose = (verbose == True)
        self.destructive = (destructive == True)

        self.client = bigquery.Client()

        print("-------------------------")
        print("BIGQUERY SERVICE...")
        print("  DATASET ADDRESS:", self.dataset_address.upper())
        print("  DESTRUCTIVE MIGRATIONS:", self.destructive)
        print("  VERBOSE QUERIES:", self.verbose)
        print("-------------------------")

        seek_confirmation()

        # did this originally, but commenting out now to prevent accidental table deletions
        # if init_tables == True:
        #     self.init_tables()

    @property
    def metadata(self):
        return {"dataset_address": self.dataset_address, "destructive": self.destructive, "verbose": self.verbose}

    @classmethod
    def cautiously_initialized(cls):
        """ DEPRECATE ME """
        service = BigQueryService()
        if APP_ENV == "development":
            print("-------------------------")
            print("BIGQUERY CONFIG...")
            print("  DATASET ADDRESS:", service.dataset_address.upper())
            print("  DESTRUCTIVE MIGRATIONS:", service.destructive)
            print("  VERBOSE QUERIES:", service.verbose)
            print("-------------------------")
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        # service.init_tables() # did this originally, but commenting out now to prevent accidental table deletions
        return service

    def init_tables(self):
        """ Creates new tables for storing follower graphs """
        self.migrate_populate_users()
        self.migrate_user_friends()

        #user_friends_table_ref = self.dataset_ref.table("user_friends")
        #self.user_friends_table = self.client.get_table(user_friends_table_ref) # an API call (caches results for subsequent inserts)
        self.user_friends_table = self.client.get_table(f"{self.dataset_address}.user_friends") # an API call (caches results for subsequent inserts)

    def execute_query(self, sql):
        """Param: sql (str)"""
        if self.verbose:
            print(sql)
        job = self.client.query(sql)
        return job.result()

    def execute_query_in_batches(self, sql, temp_table_name=None):
        """Param: sql (str)"""
        if not temp_table_name:
            temp_table_id = generate_temp_table_id()
            temp_table_name = f"{self.dataset_address}.temp_{temp_table_id}"

        # todo: consider deleting an existing temp table and then overwriting it,
        # ... or figure out a good system for deleting the temp tables after they have been created

        job_config = bigquery.QueryJobConfig(
            priority=bigquery.QueryPriority.BATCH,
            allow_large_results=True,
            destination=temp_table_name
        )
        job = self.client.query(sql, job_config=job_config)
        print("BATCH QUERY JOB:", type(job), job.job_id, job.state, job.location)
        return job

    def fetch_topics(self):
        sql = f"""
            SELECT topic, created_at
            FROM `{self.dataset_address}.topics`
            ORDER BY created_at;
        """
        return self.execute_query(sql)

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
                SELECT DISTINCT
                    user_id
                    ,user_screen_name as screen_name
                FROM `{self.dataset_address}.tweets`
                WHERE user_id IS NOT NULL AND user_screen_name IS NOT NULL
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
                friend_count INT64,
                friend_names ARRAY<STRING>,
                start_at TIMESTAMP,
                end_at TIMESTAMP
            );
        """
        results = self.execute_query(sql)
        return list(results)

    #
    # COLLECTING USER FRIENDS
    #

    def fetch_remaining_users(self, min_id=None, max_id=None, limit=None):
        """Returns a list of table rows"""
        sql = f"""
            SELECT
                u.user_id
                ,u.screen_name
            FROM `{self.dataset_address}.users` u
            LEFT JOIN `{self.dataset_address}.user_friends` f ON u.user_id = f.user_id
            WHERE f.user_id IS NULL
        """
        if min_id and max_id:
            sql += f"  AND CAST(u.user_id as int64) BETWEEN {int(min_id)} AND {int(max_id)} "
        sql += f"ORDER BY u.user_id "
        if limit:
            sql += f"LIMIT {int(limit)};"
        results = self.execute_query(sql)
        return list(results)

    def insert_user_friends(self, records):
        """
        Param: records (list of dictionaries)
        """
        rows_to_insert = [list(d.values()) for d in records]
        #rows_to_insert = [list(d.values()) for d in records if any(d["friend_names"])] # doesn't store failed attempts. can try those again later
        #if any(rows_to_insert):
        errors = self.client.insert_rows(self.user_friends_table, rows_to_insert)
        return errors

    def user_friend_collection_progress(self):
        sql = f"""
        SELECT
            count(distinct user_id) as user_count
            ,round(avg(runtime_seconds), 2) as avg_duration
            ,round(sum(has_friends) / count(distinct user_id), 2) as pct_friendly
            ,round(avg(CASE WHEN has_friends = 1 THEN runtime_seconds END), 2) as avg_duration_friendly
            ,round(avg(CASE WHEN has_friends = 1 THEN friend_count END), 2) as avg_friends_friendly
        FROM (
            SELECT
                user_id
                ,friend_count
                ,if(friend_count > 0, 1, 0) as has_friends
                ,start_at
                ,end_at
                ,DATETIME_DIFF(CAST(end_at as DATETIME), cast(start_at as DATETIME), SECOND) as runtime_seconds
            FROM `{service.dataset_address}.user_friends`
        ) subq
        """
        return self.execute_query(sql)

    #
    # FRIEND GRAPHS
    #

    def fetch_user_friends(self, min_id=None, max_id=None, limit=None):
        sql = f"""
            SELECT user_id, screen_name, friend_count, friend_names, start_at, end_at
            FROM `{self.dataset_address}.user_friends`
        """
        if min_id and max_id:
            sql += f" WHERE CAST(user_id as int64) BETWEEN {int(min_id)} AND {int(max_id)} "
        sql += f"ORDER BY user_id "
        if limit:
            sql += f"LIMIT {int(limit)};"
        #return list(self.execute_query(sql))
        return self.execute_query(sql) # return the generator so we can avoid storing the results in memory

    def fetch_user_friends_in_batches(self, limit=None):
        sql = f"""
            SELECT user_id, screen_name, friend_count, friend_names
            FROM `{self.dataset_address}.user_friends`
        """
        if limit:
            sql += f"LIMIT {int(limit)};"

        self.execute_query_in_batches(sql)

    def partition_user_friends(self, n=10):
        """Params n (int) the number of partitions, each will be of equal size"""
        sql = f"""
            SELECT
                partition_id
                ,count(DISTINCT user_id) as user_count
                ,min(user_id) as min_id
                ,max(user_id) as max_id
            FROM (
            SELECT
                NTILE({int(n)}) OVER (ORDER BY CAST(user_id as int64)) as partition_id
                ,CAST(user_id as int64) as user_id
            FROM (SELECT DISTINCT user_id FROM `{self.dataset_address}.user_friends`)
            ) user_partitions
            GROUP BY partition_id
        """
        results = self.execute_query(sql)
        return list(results)

    def fetch_random_users(self, limit=1000, topic="impeach", start_at=DEFAULT_START, end_at=DEFAULT_END):
        """
        Fetches a random slice of users talking about a given topic during a given timeframe.

        Params:

            topic (str) the topic they were tweeting about:
                        to be balanced, choose 'impeach', '#IGHearing', '#SenateHearing', etc.
                        to be left-leaning, choose '#ImpeachAndConvict', '#ImpeachAndRemove', etc.
                        to be right-leaning, choose '#ShamTrial', '#AquittedForever', '#MAGA', etc.

            limit (int) the max number of users to fetch

            start_at (str) a date string for the earliest tweet

            end_at (str) a date string for the latest tweet

        """
        sql = f"""
            SELECT DISTINCT user_id, user_screen_name, user_created_at
            FROM `{self.dataset_address}.tweets`
            WHERE upper(status_text) LIKE '%{topic.upper()}%' AND (created_at BETWEEN '{start_at}' AND '{end_at}')
            ORDER BY rand()
            LIMIT {int(limit)};
        """
        return self.execute_query(sql)

    #
    # RETWEET GRAPHS
    #

    def fetch_retweet_counts_in_batches(self, topic=None, start_at=None, end_at=None):
        """
        For each retweeter, includes the number of times each they retweeted each other user.
            Optionally about a given topic.
            Optionally with within a given timeframe.

        Params:

            topic (str) the topic they were tweeting about, like 'impeach', '#MAGA', "@politico", etc.
            start_at (str) a date string for the earliest tweet
            end_at (str) a date string for the latest tweet
        """
        sql = f"""
            SELECT
                user_id
                ,user_screen_name
                ,retweet_user_screen_name
                ,count(distinct status_id) as retweet_count
            FROM `{self.dataset_address}.retweets`
            WHERE user_screen_name <> retweet_user_screen_name -- excludes people retweeting themselves
        """
        if topic:
            sql+=f"""
                AND upper(status_text) LIKE '%{topic.upper()}%'
            """
        if start_at and end_at:
            sql+=f"""
                AND (created_at BETWEEN '{start_at}' AND '{end_at}')
            """
        sql += """
            GROUP BY 1,2,3
        """

        self.execute_query_in_batches(sql)


    def fetch_specific_user_friends(self, screen_names):
        sql = f"""
            SELECT user_id, screen_name, friend_count, friend_names, start_at, end_at
            FROM `{self.dataset_address}.user_friends`
            WHERE screen_name in {tuple(screen_names)} -- tuple conversion surrounds comma-separated screen_names in parens
        """
        return self.execute_query(sql)

    def fetch_specific_retweet_counts(self, screen_names):
        """FYI this fetches multiple rows per screen_name, for each screen_name that user retweeted"""
        sql = f"""
            SELECT user_id, user_screen_name, retweet_user_screen_name, retweet_count
            FROM `{self.dataset_address}.retweet_counts`
            WHERE user_screen_name in {tuple(screen_names)} -- tuple conversion surrounds comma-separated screen_names in parens
                -- AND user_screen_name <> retweet_user_screen_name -- exclude users who have retweeted themselves
            ORDER BY 2,3
        """
        return self.execute_query(sql)

    def fetch_retweet_weeks(self, start_at=None, end_at=None):
        """
        Params:
            start_at (str) like "2019-12-15 00:00:00"
            end_at (str) like "2020-03-21 23:59:59"
        """
        sql = f"""
            SELECT
                CASE
                    WHEN EXTRACT(week from created_at) = 0 THEN EXTRACT(year from created_at) - 1 -- treat first week of new year as the previous year
                    ELSE EXTRACT(year from created_at)
                    END  year

                ,CASE
                    WHEN EXTRACT(week from created_at) = 0 THEN 52 -- treat first week of new year as the previous week
                    ELSE EXTRACT(week from created_at)
                    END  week

                ,count(DISTINCT EXTRACT(day from created_at)) as day_count
                ,min(created_at) as min_created
                ,max(created_at) as max_created
                ,count(DISTINCT status_id) as retweet_count
                ,count(DISTINCT user_id) as user_count
            FROM `{self.dataset_address}.retweets`
        """
        if start_at and end_at:
            sql += f"""
            WHERE created_at BETWEEN '{start_at}' AND '{end_at}'
            """
        sql += """
            GROUP BY 1,2
            ORDER BY 1,2
        """
        return self.execute_query(sql)

    #
    # LOCAL ANALYSIS
    #

    def fetch_user_details_in_batches(self, limit=None):
        sql = f"""
            SELECT
                user_id
                ,screen_name
                ,name
                ,description
                ,location
                ,verified
                ,created_at

                ,screen_name_count
                ,name_count
                ,description_count
                ,location_count
                ,verified_count
                ,created_at_count

                ,screen_names
                ,names
                ,descriptions
                ,locations
                ,verifieds
                ,created_ats

                ,friend_count

                ,status_count
                ,retweet_count

                -- these topics are specific to the impeachment dataset, so will need to generalize if/when working with another topic (leave for future concern)
                ,impeach_and_convict
                ,senate_hearing
                ,ig_hearing
                ,facts_matter
                ,sham_trial
                ,maga
                ,acquitted_forever

            FROM `{self.dataset_address}.user_details`
        """
        if limit:
            sql += f"LIMIT {int(limit)};"

        self.execute_query_in_batches(sql)

    def fetch_retweeter_details_in_batches(self, limit=None):
        sql = f"""
            SELECT
                user_id

                ,verified
                ,created_at
                ,screen_name_count
                ,name_count

                ,retweet_count
                ,ig_report
                ,ig_hearing
                ,senate_hearing
                ,not_above_the_law
                ,impeach_and_convict
                ,impeach_and_remove
                ,facts_matter
                ,sham_trial
                ,maga
                ,acquitted_forever
                ,country_over_party

            FROM `{self.dataset_address}.retweeter_details`
        """
        if limit:
            sql += f"LIMIT {int(limit)};"

        self.execute_query_in_batches(sql)

    def fetch_retweeters_by_topic_exclusive(self, topic):
        """
        Get the retweeters talking about topic x and those not, so we can perform a two-sample KS-test on them.
        """
        topic = topic.upper() # do uppercase conversion once here instead of many times inside sql below
        sql = f"""
            -- TOPIC: '{topic}'
            SELECT
                rt.user_id
                ,rt.user_created_at
                ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '{topic}') then rt.status_id end) as count
            FROM {self.dataset_address}.retweets rt
            GROUP BY 1,2
        """
        return self.execute_query(sql)

    def fetch_retweeters_by_topics_exclusive(self, x_topic, y_topic):
        """
        Get the retweeters talking about topic x and not y (and vice versa).
        For each user, determines how many times they were talking about topic x and y.
        Only returns users who were talking about one or the other, so we can perform a two-sample KS-test on them.
        """
        x_topic = x_topic.upper() # do uppercase conversion once here instead of many times inside sql below
        y_topic = y_topic.upper() # do uppercase conversion once here instead of many times inside sql below
        sql = f"""
            -- TOPICS: '{x_topic}' | '{y_topic}'
            SELECT
                rt.user_id
                ,rt.user_created_at
                ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '{x_topic}') then rt.status_id end) as x_count
                ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '{y_topic}') then rt.status_id end) as y_count
            FROM {self.dataset_address}.retweets rt
            WHERE REGEXP_CONTAINS(upper(rt.status_text), '{x_topic}')
                OR REGEXP_CONTAINS(upper(rt.status_text), '{y_topic}')
            GROUP BY 1,2
            HAVING (x_count > 0 and y_count = 0) OR (x_count = 0 and y_count > 0) -- mutually exclusive populations
        """
        return self.execute_query(sql)


class RetweetWeek:
    def __init__(self, row):
        """
        A decorator for the rows returned by the fetch_retweet_weeks() query.

        Param row (google.cloud.bigquery.table.Row)
        """
        self.row = row

    @property
    def week_id(self):
        return f"{self.row.year}-{str(self.row.week).zfill(2)}" #> "2019-52", "2020-01", etc.

    @property
    def details(self):
        details = ""
        details += f"ID: {self.week_id} | "
        details += f"FROM: '{dt_to_date(self.row.min_created)}' "
        details += f"TO: '{dt_to_date(self.row.max_created)}' | "
        details += f"DAYS: {fmt_n(self.row.day_count)} | "
        details += f"USERS: {fmt_n(self.row.user_count)} | " + f"RETWEETS: {fmt_n(self.row.retweet_count)}"
        return details

if __name__ == "__main__":

    service = BigQueryService.cautiously_initialized()

    print("--------------------")
    print("FETCHED TOPICS:")
    print([row.topic for row in service.fetch_topics()])

    sql = f"SELECT count(distinct status_id) as tweet_count FROM `{service.dataset_address}.tweets`"
    results = service.execute_query(sql)
    print("--------------------")
    tweet_count = list(results)[0].tweet_count
    print(f"FETCHED {fmt_n(tweet_count)} TWEETS")

    print("--------------------")
    sql = f"SELECT count(distinct user_id) as user_count FROM `{service.dataset_address}.tweets`"
    results = service.execute_query(sql)
    user_count = list(results)[0].user_count
    print(f"FETCHED {fmt_n(user_count)} USERS")

    results = service.user_friend_collection_progress()
    row = list(results)[0]
    collected_count = row.user_count
    pct = collected_count / user_count
    #print("--------------------")
    #print("USERS COLLECTED:", collected_count)
    #print("  PCT COLLECTED:", f"{(pct * 100):.1f}%")
    #print("  AVG DURATION:", row.avg_duration)
    if collected_count > 0:
        print("--------------------")
        print(f"USERS WITH FRIENDS: {row.pct_friendly * 100}%")
        print("  AVG FRIENDS:", round(row.avg_friends_friendly))
        #print("  AVG DURATION:", row.avg_duration_friendly)
