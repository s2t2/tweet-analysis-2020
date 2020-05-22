
import time
import os
from datetime import datetime as dt
import psycopg2
from networkx import DiGraph, write_gpickle

from app import DATA_DIR, APP_ENV
from app.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
from app.workers import BATCH_SIZE, DRY_RUN, generate_timestamp

class BaseGrapher():
    def __init__(self, database_url=DATABASE_URL, table_name=USER_FRIENDS_TABLE_NAME, batch_size=BATCH_SIZE, dry_run=DRY_RUN):
        self.database_url = database_url
        self.table_name = table_name
        self.batch_size = batch_size
        self.dry_run = (dry_run == True)
        self.generate_timestamp = generate_timestamp

    @classmethod
    def cautiously_initialized(cls):
        service = cls()
        print("-------------------------")
        print("NETWORK GRAPHER CONFIG...")
        print("  PG TABLE NAME:", service.table_name.upper())
        print("  BATCH SIZE:", service.batch_size)
        print("  DRY RUN:", str(service.dry_run).upper())
        print("-------------------------")
        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        return service

    @property
    def sql(self):
        return f"SELECT id, user_id, screen_name, friend_count, friend_names FROM {self.table_name};"

    def perform(self):
        """ TODO: have any child perform method automatically wrapped with start() and end() invocations
        Override this method in the child class. Make sure to:
            1. Invoke self.start()
            2. Assemble the DiGraph() as self.graph
            3. Invoke self.end()
        """
        self.start()
        self.graph = DiGraph()
        self.end()

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor(name="network_grapher", cursor_factory=psycopg2.extras.DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!
        self.start_at = time.perf_counter()
        self.counter = 0

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.cursor.close()
        self.connection.close()
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {self.counter} USERS IN {self.duration_seconds} SECONDS")
        self.report()

    def report(self):
        print("NODES:", len(self.graph.nodes))
        print("EDGES:", len(self.graph.edges))
        print("SIZE:", self.graph.size())

    def write_to_file(self, graph_filepath=None):
        if not graph_filepath:
            timestamp = dt.now().strftime("%Y_%m_%d_%H_%M")
            graph_filepath = os.path.join(DATA_DIR, f"follower_network_{timestamp}.gpickle")

        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)

if __name__ == "__main__":

    grapher = BaseGrapher.cautiously_initialized()
    grapher.perform()
