
from memory_profiler import profile

from networkx import DiGraph

from app import seek_confirmation
from app.job import Job
from app.bq_service import BigQueryService
from app.bot_impact.daily_friend_graph_storage import DailyFriendGraphStorage as GraphStorage

DATE = os.getenv("DATE", default="2020-02-05")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1000"))

class DailyFriendGrapher(GraphStorage, Job):
    def __init__(self, bq_service=None, date=DATE, batch_size=BATCH_SIZE):
        self.bq_service = bq_service or BigQueryService()
        self.date = date
        self.batch_size = batch_size

        Job.__init__(self)
        GraphStorage.__init__(self, dirpath=f"daily_friend_graphs/{self.date}")

        print("-------------------------")
        print("DAILY FRIEND GRAPHER...")
        print("  DATE:", self.date)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"date": self.date, "batch_size": self.batch_size}}

    @profile
    def perform(self):
        self.start()
        self.graph = DiGraph()

        print("FETCHING TWEETERS AND THEIR FRIENDS...")

        for row in self.bq_service.fetch_tweeter_friend_lists(date=self.date):
            user_id = row["user_id"]
            self.graph.add_edges_from([(user_id, friend_id) for friend_id in row["friend_ids"]])

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

    grapher.subgraph_report()
    grapher.save_subgraph()
