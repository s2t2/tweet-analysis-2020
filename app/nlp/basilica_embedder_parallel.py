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

def split_into_batches(all_records, batch_size):
    for i in range(0, len(all_records), batch_size):
        yield all_records[i : i + batch_size]

def perform(batch):
    bq_service = BigQueryService()
    bas_service = BasilicaService()

    embeddings = list(bas_service.embed_tweets([row["status_text"] for row in batch]))

    for i, row in enumerate(batch):
        row["embedding"] = embeddings[i]
        del row["status_text"]

    bq_service.upload_basilica_embeddings(batch)
    print("UPLOAD COMPLETE!")


if __name__ == "__main__":

    print("-------------------")
    print("BASILICA EMBEDDER...")
    print("  LIMIT:", LIMIT)
    print("  BATCH SIZE:", BATCH_SIZE)

    records = bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT)

    batches = split_into_batches(records, BATCH_SIZE)
    print(len(batches))

    exit()

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        #for batch in batches:
        #    executor.submit(perform, batch)

        futures = [executor.submit(perform, batch) for batch in batches]
        for future in as_completed(futures):
            future.result()
