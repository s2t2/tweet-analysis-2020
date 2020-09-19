
import os
from memory_profiler import profile

from networkx import DiGraph

from app import seek_confirmation
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
    def compile_graph(self):
        self.start()
        self.graph = DiGraph()

        print("FETCHING TWEETERS AND THEIR FRIENDS...")

        for row in self.bq_service.fetch_daily_user_friends_for_active_tweeters(date=self.date, tweet_min=self.tweet_min, limit=self.limit):
            self.graph.add_edges_from([(row["screen_name"], friend_name) for friend_name in row["friend_names"]])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()
        self.end()

    @profile
    def compile_subgraph(self):
        #breakpoint()
        pass



if __name__ == "__main__":

    # for all tweets on a given day,
    # ... assemble a friend graph between all ACTIVE tweeters and the people they follow
    # ... with edge format: (follower, following1)
    # ... and save to gpickle and upload to GCS
    # ... also create a subgraph and save to gpickle and upload to GCS:

    grapher = DailyFriendGrapher()
    grapher.save_metadata()

    grapher.compile_graph()
    grapher.graph_report()
    grapher.save_graph()

    grapher.compile_subgraph()
    grapher.subgraph_report()
    grapher.save_subgraph()
