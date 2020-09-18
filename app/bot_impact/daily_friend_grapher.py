
import os
from memory_profiler import profile

from networkx import DiGraph

from app import seek_confirmation
from app.job import Job
from app.bq_service import BigQueryService
from app.bot_impact.friend_graph_storage import FriendGraphStorage

DATE = os.getenv("DATE", default="2020-02-05")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1000"))
LIMIT = os.getenv("LIMIT") # default none, but maybe use 10000

class DailyFriendGrapher(FriendGraphStorage, Job):
    def __init__(self, bq_service=None, date=DATE, batch_size=BATCH_SIZE, limit=LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.date = date
        self.batch_size = batch_size
        self.limit = limit

        Job.__init__(self)
        FriendGraphStorage.__init__(self, dirpath=f"daily_friend_graphs/{self.date}")

        print("-------------------------")
        print("DAILY FRIEND GRAPHER...")
        print("  DATE:", self.date)
        print("  LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"bq_service": self.bq_service.metadata, "date": self.date, "batch_size": self.batch_size, "limit":self.limit}}

    @profile
    def perform(self):
        self.start()
        #self.edges = set()
        self.graph = DiGraph()

        print("FETCHING TWEETERS AND THEIR FRIENDS...")
        for row in self.bq_service.fetch_tweeter_friend_lists(date=self.date, limit=self.limit):
            user = row["user_screen_name"].upper()
            #print(user, row["friend_count"])

            #self.edges.update([(user, friend.upper()) for friend in row["friend_names"]])
            self.graph.add_edges_from([(user, friend.upper()) for friend in row["friend_names"]])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()

        self.end()


if __name__ == "__main__":

    # for all tweets on a given day,
    # ... assemble a friend graph between all tweeters and the people they follow
    # ... with edge format: (follower, following1)
    # ... and save to gpickle and upload to GCS
    # ... also create a subgraph and save to gpickle and upload to GCS:

    grapher = DailyFriendGrapher()
    grapher.save_metadata()

    grapher.perform()

    grapher.graph_report()
    grapher.save_graph()

    #breakpoint()
    #grapher.subgraph_report()
    #grapher.save_subgraph()
