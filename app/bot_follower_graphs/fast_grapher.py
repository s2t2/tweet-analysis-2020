




import os
#from datetime import datetime
#import time
from functools import lru_cache

from memory_profiler import profile
from dotenv import load_dotenv
from networkx import DiGraph
import psycopg2


from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import logstamp

from app.bq_service import BigQueryService
from app.pg_pipeline.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.job import Job

load_dotenv()

BOT_MIN = float(os.getenv("BOT_MIN", default="0.8"))

DRY_RUN = (os.getenv("DRY_RUN", default="false") == "true")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1000")) # it doesn't refer to the size of the batches fetched from BQ but rather the interval at which to take a reporting snapshot, which gets compiled and written to CSV. set this to a very large number like 25000 to keep memory costs down, if that's a concern for you.
USERS_LIMIT = os.getenv("USERS_LIMIT")

class PgService:
    def __init__(self, database_url=DATABASE_URL):
        self.database_url = database_url
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor(name="follower_grapher", cursor_factory=psycopg2.extras.DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!

        print("-------------------------")
        print("PG SERVICE")
        print(f"  DATABASE URL: '{self.database_url.upper()}")
        print("  CONNECTION:", type(self.connection))
        print("  CURSOR:", type(self.cursor), self.cursor.name)

    def fetch_user_friends(self, limit=None):
        sql = f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {USER_FRIENDS_TABLE_NAME} "
        if limit:
            sql += f" LIMIT {int(limit)};"
        self.cursor.execute(sql)

    def clean_up(self):
        print("CLEANING UP...")
        self.cursor.close()
        self.connection.close()

class BotFollowerGrapher(GraphStorage, Job):

    def __init__(self, bot_min=BOT_MIN, batch_size=BATCH_SIZE, users_limit=USERS_LIMIT, storage_dirpath=None, bq_service=None, pg_service=None):
        """
        Gets all bots classified above a given threshold.
        Then creates a directed graph with edges between each bot and each of their followers, like: (follower_id, bot_id)
        """

        Job.__init__(self)

        self.batch_size = int(batch_size)

        self.users_limit = users_limit
        if self.users_limit:
            self.users_limit = int(self.users_limit)

        self.bot_min = float(bot_min)
        storage_dirpath = storage_dirpath or f"bot_follower_graphs/bot_min/{self.bot_min}"
        GraphStorage.__init__(self, dirpath=storage_dirpath)

        self.bq_service = bq_service or BigQueryService() # todo: remove
        self.pg_service = pg_service or PgService()

        print("-------------------------")
        print("BOT FOLLOWER GRAPHER...")
        print("  BOT MIN:", self.bot_min)
        print("  BATCH SIZE:", self.batch_size)
        print("  USERS LIMIT:", self.users_limit)
        print("  DRY RUN:", DRY_RUN)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"bot_min": self.bot_min, "batch_size": self.batch_size, "database_url": self.pg_service.database_url, "table_name": USER_FRIENDS_TABLE_NAME}}

    @property
    @lru_cache(maxsize=None)
    def bots(self):
        return list(self.bq_service.fetch_bots(bot_min=self.bot_min)) # TODO: convert to PG

    @property
    @lru_cache(maxsize=None)
    def bot_names(self):
        return [bot["bot_screen_name"].upper() for bot in self.bots]

    @profile
    def perform(self):
        self.graph = DiGraph()

        print("FETCHED BOTS:", len(self.bots))

        print("FETCHING USER FRIENDS IN BATCHES...")
        self.pg_service.fetch_user_friends(limit=self.users_limit)
        while True:
            batch = self.pg_service.cursor.fetchmany(size=self.batch_size)
            if not batch: break
            self.process_batch(batch)
            self.counter += len(batch)
            print("  ", logstamp(), fmt_n(self.counter), "| NODES:", fmt_n(self.node_count), "| EDGES:", fmt_n(self.edge_count))

        self.pg_service.clean_up()

    def process_batch(self, batch):
        for follower in batch:
            friend_names = [friend_name.upper() for friend_name in follower["friend_names"]]
            follows_bot_names = set(friend_names) & set(self.bot_names) # intersection of two sets

            if any(follows_bot_names):
                bots_followed = [bot for bot in self.bots if bot["bot_screen_name"].upper() in follows_bot_names]
                #self.graph.add_edges_from([(follower["user_id"], bot["bot_id"]) for bot in bots_followed])




if __name__ == "__main__":

    grapher = BotFollowerGrapher()
    grapher.save_metadata()

    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()

    grapher.save_graph()
