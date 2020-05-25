
import time
import os
from datetime import datetime as dt
import pickle

from networkx import DiGraph, write_gpickle
from pandas import DataFrame

from app import APP_ENV
from app.workers import BATCH_SIZE, DRY_RUN, fmt_ts, fmt_n

class BaseGrapher():
    """
    Example:
        grapher = BaseGrapher.cautiously_initialized()
        grapher.start()
        grapher.perform()
        grapher.end()
        grapher.report()
    """

    def __init__(self, dry_run=DRY_RUN, batch_size=BATCH_SIZE):
        self.job_id = dt.now().strftime("%Y-%m-%d-%H%M") # a timestamp-based unique identifier, should be able to be included in a filepath, associates multiple files produced by the job with each other
        self.dry_run = (dry_run == True)
        self.batch_size = batch_size

    @classmethod
    def cautiously_initialized(cls):
        service = cls()
        print("-------------------------")
        print("NETWORK GRAPHER CONFIG...")
        print("  JOB ID:", service.job_id)
        print("  DRY RUN:", str(service.dry_run).upper())
        print("  BATCH SIZE:", str(service.batch_size).upper())
        print("-------------------------")
        if APP_ENV == "development":
            if input("CONTINUE? (Y/N): ").upper() != "Y":
                print("EXITING...")
                exit()
        return service

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.start_at = time.perf_counter()
        self.counter = 0

    def perform(self):
        self.graph = DiGraph()

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {fmt_n(self.counter)} USERS IN {fmt_n(self.duration_seconds)} SECONDS")

    def report(self):
        print("NODES:", fmt_n(len(self.graph.nodes)))
        print("EDGES:", fmt_n(len(self.graph.edges)))
        print("SIZE:", fmt_n(self.graph.size()))

if __name__ == "__main__":

    grapher = BaseGrapher.cautiously_initialized()
    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
