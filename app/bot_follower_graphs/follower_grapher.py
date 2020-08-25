




import os
#from datetime import datetime
#import time
#from functools import lru_cache

from memory_profiler import profile
from dotenv import load_dotenv
from networkx import DiGraph

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import logstamp

from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.job import Job

load_dotenv()

BOT_MIN = float(os.getenv("BOT_MIN", default="0.8"))

DRY_RUN = (os.getenv("DRY_RUN", default="false") == "true")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25000")) # it doesn't refer to the size of the batches fetched from BQ but rather the interval at which to take a reporting snapshot, which gets compiled and written to CSV. set this to a very large number like 25000 to keep memory costs down, if that's a concern for you.

class BotFollowerGrapher(GraphStorage, Job):

    def __init__(self, bot_min=BOT_MIN, batch_size=BATCH_SIZE, storage_dirpath=None, bq_service=None):
        Job.__init__(self)
        self.bot_min = float(bot_min)
        self.batch_size = int(batch_size)

        storage_dirpath = storage_dirpath or f"bot_follower_graphs/bot_min/{self.bot_min}"
        GraphStorage.__init__(self, dirpath=storage_dirpath)

        self.bq_service = bq_service or BigQueryService()

        print("-------------------------")
        print("BOT FOLLOWER GRAPHER...")
        print("  BOT MIN:", self.bot_min)
        print("  BATCH SIZE:", self.batch_size)
        print("  DRY RUN:", DRY_RUN)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"bot_min": self.bot_min, "batch_size": self.batch_size}}

    def perform(self):
        """
        Gets all bots classified above a given threshold.
            Then for each bot: gets a list of their followers, and
            creates a directed graph with edges between each bot and each user that follows, like:

            edge = (follower_id, bot_id)
        """
        self.results = []
        self.graph = DiGraph()

        bot_screen_names = [row.bot_screen_name for row in list(self.bq_service.fetch_bots(bot_min=self.bot_min))]
        bot_screen_names = list(set(bot_screen_names)) # de-dup for good measure
        print("BOTS:", len(bot_screen_names))

        seek_confirmation()

        for bot_screen_name in bot_screen_names:
            # yeah we're doing a query per bot. there are about 1000 bots total. ideally we'd do a single query
            for row in self.bq_service.fetch_user_followers_by_screen_name(bot_screen_name):

                breakpoint()

                self.graph.add_edge(row["follower_id"], row["bot_id"])

                self.counter += 1
                if self.counter % self.batch_size == 0:
                    print("COUNTER:", self.counter)


if __name__ == "__main__":

    grapher = BotFollowerGrapher()

    grapher.perform()
