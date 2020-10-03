
import os

from networkx import DiGraph, write_gpickle, read_gpickle
from memory_profiler import profile

from app import seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.job import Job
from app.bq_service import BigQueryService
from app.file_storage import FileStorage

START_DATE = os.getenv("START_DATE", default="2020-01-01") # includes tweets on this date
END_DATE = os.getenv("END_DATE", default="2021-02-01")  # excludes tweets on this date (pick the date after the one you need to cover)
TOPIC = os.getenv("TOPIC") # optional

LIMIT = os.getenv("USERS_LIMIT") # optional
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="10000"))

class RetweetGrapher(Job):
    def __init__(self, start_date=START_DATE, end_date=END_DATE, topic=TOPIC, limit=LIMIT, batch_size=BATCH_SIZE):
        self.start_date = start_date
        self.end_date = end_date
        self.topic = topic
        self.limit = limit
        self.batch_size = batch_size

        self.bq_service = BigQueryService()

        #self.storage = FileStorage(dirpath=f"retweet_graphs_v3/topic/{self.topic}/date_range/{self.start_date}--{self.end_date}")
        dirpath = f"retweet_graphs_v3/date_range/{self.start_date}--{self.end_date}"
        if self.topic: dirpath += "/topic/{self.topic}"
        self.storage = FileStorage(dirpath=dirpath)

        self.local_graph_filepath = os.path.join(self.storage.local_dirpath, "graph.gpickle")
        self.gcs_graph_filepath = os.path.join(self.storage.gcs_dirpath, "graph.gpickle")

        print("-------------------------")
        print("RETWEET GRAPHER...")
        print("  START DATE:", self.start_date)
        print("  END DATE:", self.end_date)
        print("  TOPIC:", self.topic)
        print("  LIMIT:", self.limit)
        print("  BATCH SIZE:", self.batch_size)

        seek_confirmation()

    @property
    def metadata(self):
        return {
            "bq_service": self.bq_service.metadata,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "topic": self.topic,
            "limit": self.limit,
            "batch_size": self.batch_size
        }

    def construct_graph(self):
        self.start()
        print("CONSTRUCTING GRAPH...")
        self.graph = DiGraph()
        for row in self.bq_service.fetch_retweet_edges_v3(start_at=self.start_date, end_at=self.end_date, topic=self.topic):
            self.graph.add_edge(row["user_id"], row["retweeted_user_id"], weight=row["retweet_count"])

            self.counter +=1
            if self.counter % self.batch_size == 0:
                self.progress_report()

        self.end()
        print(type(self.graph), fmt_n(self.graph.number_of_nodes()), fmt_n(self.graph.number_of_edges()))

    def save_graph(self):
        print("SAVING GRAPH...")
        write_gpickle(self.graph, self.local_graph_filepath)
        self.storage.upload_file(self.local_graph_filepath, self.gcs_graph_filepath)

    @profile
    def load_graph(self):
        print("LOADING GRAPH...")
        if not os.path.exists(self.local_graph_filepath):
            self.storage.download_file(self.gcs_graph_filepath, self.local_graph_filepath)
        return read_gpickle(self.local_graph_filepath)

if __name__ == "__main__":

    grapher = RetweetGrapher()
    #grapher.save_metadata()
    grapher.construct_graph()
    grapher.save_graph()
    #grapher.save_metadata()
