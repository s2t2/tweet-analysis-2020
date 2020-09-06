import os

from app import seek_confirmation
from app.job import Job
from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage, MODELS_DIRPATH

MODEL_NAME = os.getenv("MODEL_NAME", default="current_best")

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))

if __name__ == "__main__":

    storage = ModelStorage(dirpath=f"{MODELS_DIRPATH}/{MODEL_NAME}")
    tv = storage.load_vectorizer()
    clf = storage.load_model()

    bq_service = BigQueryService()

    print("DESTROYING PREDICTIONS TABLE???")
    seek_confirmation()
    print("DESTROYING PREDICTIONS TABLE...")
    bq_service.destructively_migrate_2_community_predictions_table()

    job = Job()
    job.start()

    ids_batch = []
    statuses_batch = []
    for row in bq_service.fetch_unlabeled_statuses_in_batches(limit=LIMIT):
        ids_batch.append(row["status_id"])
        statuses_batch.append(row["status_text"])

        job.counter += 1
        if job.counter % BATCH_SIZE == 0:
            results = clf.predict(tv.transform(statuses_batch))
            batch = [{"status_id": status_id, "community_id":int(i)} for status_id, i in zip(ids_batch, results)]
            bq_service.upload_predictions_in_batches(batch)

            job.progress_report()
            ids_batch = []
            statuses_batch = []
            batch = []

    if len(statuses_batch) > 0:
        results = clf.predict(tv.transform(statuses_batch))
        batch = [{"status_id": status_id, "community_id":int(i)} for status_id, i in zip(ids_batch, results)]
        bq_service.upload_predictions_in_batches(batch)

        job.progress_report()
        ids_batch = []
        statuses_batch = []
        batch = []

    job.end()
