import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import current_thread #, #Thread, Lock, BoundedSemaphore

from app.job import Job
from app.bq_service import BigQueryService
from app.basilica_service import BasilicaService

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000"))

PARALLEL = (os.getenv("PARALLEL", default="true") == "true")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", default=10))

class BasilicaEmbedder(Job):
    def __init__(self):
        self.bq_service = BigQueryService()
        self.bas_service = BasilicaService()

        print("-------------------")
        print("BASILICA EMBEDDER...")
        print("  LIMIT:", LIMIT)
        print("  BATCH SIZE:", BATCH_SIZE)

        Job.__init__(self)

if __name__ == "__main__":

    job = Embedder()
    batch = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        for row in job.bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT):
            batch.append(dict(row))

            batch_size = len(self.batch)
            if batch_size >= BATCH_SIZE: # FULL BATCH
                self.counter += batch_size
                self.save_batch(self.batch)
                self.batch = []
                self.progress_report()

        for batch in batches:
            executor.submit(perform, batch)


        #futures = [executor.submit(perform, batch) for batch in batches]
        #for future in as_completed(futures):
        #    result = future.result()
