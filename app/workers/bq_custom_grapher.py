
import os

from networkx import DiGraph
from memory_profiler import profile
from dotenv import load_dotenv

#from app.workers import fmt_ts, fmt_n
from app.workers.bq_grapher import BigQueryGrapher

load_dotenv()

USERS_LIMIT = int(os.getenv("USERS_LIMIT", default="1000")) # forces us to have a limit, unlike the app.workers version
TOPIC = os.getenv("TOPIC", default="#MAGA")
START_AT = os.getenv("START_AT", default="2019-01-15 01:00:00") # On 1/15, The House of Representatives names seven impeachment managers and votes to transmit articles of impeachment to the Senate
END_AT = os.getenv("END_AT", default="2020-01-30 01:00:00")

class BigQueryCustomGrapher(BigQueryGrapher):

    def __init__(self, users_limit=USERS_LIMIT, topic=TOPIC, start_at=START_AT, end_at=END_AT, bq_service=None, gcs_service=None):
        super().__init__(bq_service=bq_service, gcs_service=gcs_service)
        self.users_limit = users_limit
        self.topic = topic
        self.start_at = start_at
        self.end_at = end_at

        print("---------------------------------------")
        print("CUSTOM GRAPHER...")
        print(f"  FETCHING {self.users_limit} USERS")
        print(f"  TALKING ABOUT '{self.topic.upper()}' ")
        print(f"  BETWEEN '{self.start_at} AND '{self.end_at}'")

    @property
    def metadata(self):
        return {**super().metadata, **{"customizations": {
            "users_limit": self.users_limit,
            "topic": self.topic,
            "start_at": self.start_at,
            "end_at": self.end_at,
        }}} # merges dicts

    @profile
    def perform(self):
        self.write_metadata_to_file()
        self.upload_metadata()

        self.start()
        self.graph = DiGraph()

        screen_names = list(self.bq_service.fetch_random_users(limit=USERS_LIMIT, topic=TOPIC, start_at=START_AT, end_at=END_AT))
        print("FETCHED", len(screen_names), "USERS")

        #for row in self.bq_service.fetch_specific_user_friends(screen_names=screen_names):
        #    self.graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])

        self.end()
        self.report()
        self.write_graph_to_file()
        self.upload_graph()

if __name__ == "__main__":


    grapher = BigQueryCustomGrapher.cautiously_initialized()

    grapher.perform()

    grapher.sleep()
