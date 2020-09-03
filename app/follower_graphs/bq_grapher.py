from memory_profiler import profile

from networkx import DiGraph

from app import seek_confirmation
#from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService
from app.retweet_graphs_v2.graph_storage import GraphStorage
from app.job import Job

LIMIT = 1000
BATCH_SIZE = 100

class FollowerGrapher(GraphStorage, Job):
    def __init__(self, bq_service=None, batch_size=BATCH_SIZE, limit=LIMIT, storage_dirpath=None):
        self.bq_service = bq_service or BigQueryService()
        self.limit = limit
        self.batch_size = batch_size

        Job.__init__(self)

        storage_dirpath = storage_dirpath or "follower_graphs/example"
        GraphStorage.__init__(self, dirpath=storage_dirpath)

        print("-------------------------")
        print("FOLLOWER GRAPHER...")
        print("  USERS LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)
        print("-------------------------")

        seek_confirmation()

    @property
    def metadata(self):
        return {**super().metadata, **{"batch_size": self.batch_size}}

    @profile
    def perform(self):
        self.save_metadata()
        self.graph = DiGraph()
        self.start()

        print("FETCHING FOLLOWERS...")
        for row in self.bq_service.fetch_follower_lists(limit=self.limit):
            user = row["user_screen_name"]
            self.graph.add_edges_from([(follower, user) for follower in row["follower_names"]])
            #user = row["user_id"]
            #self.graph.add_edges_from([(follower, user) for follower in row["follower_ids"]])

            self.counter += 1
            if self.counter % self.batch_size == 0:
                self.progress_report()

        self.end()
        self.report()
        self.write_graph_to_file()


if __name__ == "__main__":

    grapher = FollowerGrapher()

    grapher.perform()
