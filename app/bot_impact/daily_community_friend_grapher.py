
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

class DailyCommunityFriendGrapher(FriendGraphStorage, Job):
    def __init__(self, community_id, bq_service=None, date=DATE, batch_size=BATCH_SIZE, limit=LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.date = date
        self.community_id = community_id
        self.batch_size = batch_size
        self.limit = limit

        Job.__init__(self)
        FriendGraphStorage.__init__(self, dirpath=f"daily_2_community_friend_graphs/{self.date}/community_{self.community_id}")

        print("-------------------------")
        print("DAILY COMMUNITY FRIEND GRAPHER...")
        print("  DATE:", self.date)
        print("  COMMUNITY ID:", self.community_id)
        print("  LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{
            "bq_service": self.bq_service.metadata,
            "n_communities": 2,
            "community_id": self.community_id,
            "date": self.date,
            "batch_size": self.batch_size,
            "limit":self.limit}}

    @profile
    def perform(self):
        self.start()
        self.graph = DiGraph()

        print("FETCHING COMMUNITY TWEETERS AND THEIR FRIENDS...")

        for row in self.bq_service.fetch_daily_community_friends(date=self.date, community_id=self.community_id, limit=self.limit):
            self.graph.add_edges_from([(row["screen_name"], friend_name) for friend_name in row["friend_names"]])
            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()
        self.end()



if __name__ == "__main__":

    for community_id in [0,1]:

        # for all tweets ABOUT A SET OF COMMUNITY_SPECTIFIC TOPICS on a given day,
        # ... assemble a friend graph between all tweeters and the people they follow
        # ... with edge format: (follower, following1)
        # ... and save to gpickle and upload to GCS
        # ... also create a subgraph and save to gpickle and upload to GCS:

        grapher = DailyCommunityFriendGrapher(community_id=community_id)
        grapher.save_metadata()

        grapher.perform()

        grapher.graph_report()
        grapher.save_graph()

        #breakpoint()
        #grapher.subgraph_report()
        #grapher.save_subgraph()
