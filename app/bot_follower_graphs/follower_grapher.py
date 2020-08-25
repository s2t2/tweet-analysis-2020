




import os
from datetime import datetime
import time

from memory_profiler import profile
from dotenv import load_dotenv
from networkx import DiGraph

from conftest import compile_mock_rt_graph
from app import APP_ENV, DATA_DIR, SERVER_NAME, SERVER_DASHBOARD_URL, seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.decorators.datetime_decorators import dt_to_s, logstamp
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.retweet_graphs_v2.job import Job
#from app.email_service import send_email

load_dotenv()

#TOPIC = os.getenv("TOPIC") # default is None
USERS_LIMIT = os.getenv("USERS_LIMIT") # default is None
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25000")) # it doesn't refer to the size of the batches fetched from BQ but rather the interval at which to take a reporting snapshot, which gets compiled and written to CSV. set this to a very large number like 25000 to keep memory costs down, if that's a concern for you.
TWEETS_START_AT = os.getenv("TWEETS_START_AT") # default is None
TWEETS_END_AT = os.getenv("TWEETS_END_AT") # default is None

DRY_RUN = (os.getenv("DRY_RUN", default="false") == "true")

class BotFollowerGrapher(GraphStorage, Job):

    def __init__(self, tweets_start_at=TWEETS_START_AT, tweets_end_at=TWEETS_END_AT, # topic=TOPIC
                        users_limit=USERS_LIMIT, batch_size=BATCH_SIZE,
                        storage_dirpath=None, bq_service=None):

        Job.__init__(self)
        GraphStorage.__init__(self, dirpath=storage_dirpath)
        self.bq_service = bq_service or BigQueryService()
        self.fetch_edges = self.bq_service.fetch_bot_follower_edges_in_batches # just being less verbose.

        # CONVERSATION PARAMS (OPTIONAL)

        self.tweets_start_at = tweets_start_at
        self.tweets_end_at = tweets_end_at

        # PROCESSING PARAMS

        self.users_limit = users_limit
        if self.users_limit:
            self.users_limit = int(self.users_limit)

        self.batch_size = int(batch_size)

        print("-------------------------")
        print("BOT FOLLOWER GRAPHER...")
        print("  USERS LIMIT:", self.users_limit)
        print("  BATCH SIZE:", self.batch_size)
        print("  DRY RUN:", DRY_RUN)
        print("-------------------------")
        print("CONVERSATION PARAMS...")
        #print("  TOPIC:", self.topic)
        print("  TWEETS START:", self.tweets_start_at)
        print("  TWEETS END:", self.tweets_end_at)

        seek_confirmation()



if __name__ == "__main__":

    pass

    # for each day from START_DATE to END_DATE

    # get all the bots on that day (above BOT_MIN=0.8)

    # for each bot, get a list of people who follow that bot
    # ... and create an edge between each bot and each user that follows
