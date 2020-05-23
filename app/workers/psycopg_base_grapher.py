
import time
import os
from datetime import datetime as dt
import pickle

import psycopg2
from networkx import DiGraph, write_gpickle

from app import DATA_DIR, APP_ENV
from app.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
from app.workers import BATCH_SIZE, DRY_RUN, generate_timestamp

class BaseGrapher():
    def __init__(self, database_url=DATABASE_URL, table_name=USER_FRIENDS_TABLE_NAME,
                        batch_size=BATCH_SIZE, dry_run=DRY_RUN, data_dir=DATA_DIR):
        self.database_url = database_url
        self.table_name = table_name
        self.batch_size = batch_size
        self.dry_run = (dry_run == True)
        self.generate_timestamp = generate_timestamp
        self.ts_id = dt.now().strftime("%Y%m%d_%H%M") # a timestamp-based unique identifier, should be able to be included in a filepath, associates multiple files produced by the job with each other
        self.data_dir = data_dir

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

    @staticmethod
    def fmt(large_number):
        """Formats a large number for printing.
        Param large_number (int) like 1000000000
        Returns (str) like '1,000,000,000'
        """
        return f"{large_number:,}"

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
        print(f"PROCESSED {self.fmt(self.counter)} USERS IN {self.fmt(self.duration_seconds)} SECONDS")

    def report(self):
        print("NODES:", self.fmt(len(self.graph.nodes)))
        print("EDGES:", self.fmt(len(self.graph.edges)))
        print("SIZE:", self.fmt(self.graph.size()))

    def write_edges_to_file(self, edges_filepath=None):
        edges_filepath = edges_filepath or os.path.join(self.data_dir, self.ts_id, "edges.gpickle")
        print("WRITING EDGES TO:", os.path.abspath(edges_filepath))
        with open(edges_filepath, "wb") as pickle_file:
            pickle.dump(self.edges, pickle_file)

    def write_graph_to_file(self, graph_filepath=None):
        graph_filepath = graph_filepath or os.path.join(self.data_dir, self.ts_id, "graph.gpickle")
        print("WRITING NETWORK GRAPH TO:", os.path.abspath(graph_filepath))
        write_gpickle(self.graph, graph_filepath)

if __name__ == "__main__":

    grapher = BaseGrapher.cautiously_initialized()
    grapher.perform()
    grapher.report()
