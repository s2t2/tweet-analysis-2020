
import os
from threading import current_thread #, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
import gc

from dotenv import load_dotenv

from app import server_sleep
from app.decorators.number_decorators import fmt_n
from app.bq_service import generate_timestamp, split_into_batches
from app.toxicity.checkpoint_scorer import ToxicityScorer

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=10)) # the max number of threads to use, for concurrent processing

class ToxicityScorerAsync(ToxicityScorer):

    def process_batch_async(self, batch):
        print("PROCESSING BATCH OF TEXTS...", generate_timestamp(), " | ", len(batch), " | ", current_thread().name)
        self.process_batch(batch)

    def perform_async(self, max_threads=MAX_THREADS):
        self.mgr.load_model_state()

        print("----------------")
        print(f"FETCHING TEXTS...")
        rows = list(self.fetch_texts())

        print(f"ASSEMBLING BATCHES...")
        batches = list(split_into_batches(rows, batch_size=self.batch_size))

        print(f"SCORING TEXTS IN BATCHES...")
        with ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="THREAD") as executor:
            #lock = BoundedSemaphore()
            futures = [executor.submit(self.process_batch_async, batch) for batch in batches]
            print("BATCHES WILL PROCESS:", len(futures))
            for future in as_completed(futures):
                #lock.acquire()
                future.result()
                #lock.release()

        print("----------------")
        print("ASYNC PERFORMANCE COMPLETE...")



if __name__ == "__main__":

    scorer = ToxicityScorerAsync()

    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    scorer.perform_async()

    print("----------------")
    print("JOB COMPLETE!")
    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    del scorer
    gc.collect()
    server_sleep(seconds=5*60) # give the server a break before restarting
