
import time

from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n

class Job():
    def __init__(self):
        self.start_at = None
        self.end_at = None
        self.duration_seconds = None
        self.counter = None # represents the number of items processed

    def start(self):
        print("-----------------")
        print("JOB STARTING!")
        self.counter = 0
        self.start_at = time.perf_counter()

    def progress_report(self):
        print(logstamp(), fmt_n(self.counter))

    def end(self):
        print("-----------------")
        print("JOB COMPLETE!")
        self.end_at = time.perf_counter()
        self.duration_seconds = round(self.end_at - self.start_at, 2)
        print(f"PROCESSED {fmt_n(self.counter)} ITEMS IN {fmt_n(self.duration_seconds)} SECONDS")

if __name__ == "__main__":

  job = Job()
  job.start()

  time.sleep(3)
  job.counter = 100

  job.end()
