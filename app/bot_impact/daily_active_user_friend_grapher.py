
import os
from memory_profiler import profile
from functools import lru_cache

from pandas import DataFrame
from networkx import DiGraph

from app import seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.job import Job
from app.bq_service import BigQueryService
from app.bot_impact.friend_graph_storage import FriendGraphStorage

DATE = os.getenv("DATE", default="2020-02-05")
TWEET_MIN = int(os.getenv("TWEET_MIN", default="4"))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1000"))
LIMIT = os.getenv("LIMIT") # default none, but maybe use 10000

class DailyFriendGrapher(FriendGraphStorage, Job):
    def __init__(self, bq_service=None, date=DATE, tweet_min=TWEET_MIN, batch_size=BATCH_SIZE, limit=LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.date = date
        self.tweet_min = tweet_min
        self.batch_size = batch_size
        self.limit = limit

        Job.__init__(self)
        FriendGraphStorage.__init__(self, dirpath=f"active_tweeter_friend_graphs/tweet_min/{self.tweet_min}/daily/{self.date}")

        self.graph = None
        self.nodes = None

        print("-------------------------")
        print("DAILY FRIEND GRAPHER...")
        print("  TWEET MIN:", self.tweet_min)
        print("  DATE:", self.date)
        print("  LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{
            "bq_service": self.bq_service.metadata,
            "tweet_min": self.tweet_min,
            "date": self.date,
            "batch_size": self.batch_size,
            "limit":self.limit
        }}

    @profile
    def fetch_nodes(self):
        self.start()
        self.nodes = []
        print("FETCHING DAILY ACTIVE TWEETERS AND THEIR FRIENDS...")
        for row in self.bq_service.fetch_daily_active_user_friends(date=self.date, tweet_min=self.tweet_min, limit=self.limit):
            #self.nodes.append({
            #    "user_id": row["user_id"],
            #    "screen_name": row["screen_name"],
            #    "status_count": row["status_count"],
            #    "prediction_count": row["prediction_count"],
            #    "mean_opinion_score": row["mean_opinion_score"],
            #    "friend_count": row["friend_count"],
            #    "friend_names": row["friend_names"],
            #    "is_bot": row["is_bot"],
            #    "tweet_rate": row["is_bot"]
            #})
            self.nodes.append(dict(row))

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()
        self.end()

    @property
    @lru_cache(maxsize=None)
    def nodes_df(self):
        if not self.nodes:
            self.fetch_nodes()
        return DataFrame(self.nodes)

    @profile
    def compile_graph(self):
        print("COMPILING FRIEND GRAPH...")
        self.start()
        self.graph = DiGraph()
        for i, row in self.nodes_df.iterrows():
            self.graph.add_edges_from([(row["screen_name"], friend_name) for friend_name in row["friend_names"]])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()
        self.end()

    @profile
    def compile_subgraph(self):
        #print("COMPILING SUB-GRAPH...")
        pass


if __name__ == "__main__":

    # for all tweets on a given day,
    # ... assemble a friend graph between all ACTIVE tweeters and the people they follow
    # ... with edge format: (follower, following1)
    # ... and save to gpickle and upload to GCS
    # ... also create a subgraph and save to gpickle and upload to GCS:

    grapher = DailyFriendGrapher()
    grapher.save_metadata()

    grapher.fetch_nodes()
    grapher.save_nodes()

    grapher.compile_graph()
    grapher.graph_report()
    grapher.save_graph()

    #grapher.compile_subgraph()
    #grapher.subgraph_report()
    #grapher.save_subgraph()
