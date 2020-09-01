import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import current_thread #, #Thread, Lock, BoundedSemaphore

from app.job import Job
from app.bq_service import BigQueryService, split_into_batches
from app.basilica_service import BasilicaService

MIN_VAL = float(os.getenv("MIN_VAL", default="0.0"))
MAX_VAL = float(os.getenv("MAX_VAL", default="1.0"))
LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000"))

PARALLEL = (os.getenv("PARALLEL", default="true") == "true")
MAX_THREADS = int(os.getenv("MAX_THREADS", default=10))

def perform(batch, bq_service, bas_service):
    print(current_thread().name)
    embeddings = list(bas_service.embed_tweets([row["status_text"] for row in batch]))

    for i, row in enumerate(batch):
        row["embedding"] = embeddings[i]
        del row["status_text"]

    bq_service.upload_basilica_embeddings(batch)
    print("UPLOAD COMPLETE!")


if __name__ == "__main__":

    print("-------------------")
    print("BASILICA EMBEDDER...")
    print("  MIN PARTITION VAL:", MIN_VAL)
    print("  MAX PARTITION VAL:", MAX_VAL)
    print("  LIMIT:", LIMIT)
    print("  BATCH SIZE:", BATCH_SIZE)

    bq_service = BigQueryService()
    bas_service = BasilicaService()

    job = Job()
    job.start()

    #records = list(bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT))
    #records = list(bq_service.fetch_basilica_embedless_statuses_in_batches(limit=LIMIT))
    #records = bq_service.fetch_basilica_embedless_statuses_in_range(min_id=MIN_ID, max_id=MAX_ID)
    records = list(bq_service.fetch_basilica_embedless_statuses_in_partition(min_val=MIN_VAL, max_val=MAX_VAL, limit=LIMIT))
    job.counter = len(records)

    batches = list(split_into_batches(records, BATCH_SIZE))
    print("BATCHES:", len(batches))

    job.end()
    del records

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        #for batch in batches:
        #    executor.submit(perform, batch)

        futures = [executor.submit(perform, batch, bq_service, bas_service) for batch in batches]
        for future in as_completed(futures):
            future.result()
