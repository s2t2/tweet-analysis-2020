import os

from app import seek_confirmation
from app.job import Job
from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage, MODELS_DIRPATH

MODEL_NAME = os.getenv("MODEL_NAME", default="current_best")

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))

if __name__ == "__main__":

    bq_service = BigQueryService()

    print("DESTROYING PREDICTIONS TABLE...")
    bq_service.destructively_migrate_2_community_predictions_table()

    storage = ModelStorage(dirpath=f"{MODELS_DIRPATH}/{MODEL_NAME}")
    tv = storage.load_vectorizer()
    clf = storage.load_model()

    job = Job()
    job.start()

    batch = []
    for row in bq_service.fetch_unlabeled_statuses_in_batches(limit=LIMIT):

        result = clf.predict(tv.transform([row["status_text"]]))

        batch.append({"status_id": row["status_id"], "community_id": int(result[0])})

        job.counter += 1
        if len(batch) >= BATCH_SIZE:
            job.progress_report()
            bq_service.upload_predictions_in_batches(batch)
            batch = []

    if len(batch) > 0:
        job.progress_report()
        bq_service.upload_predictions_in_batches(batch)
        batch = []

    job.end()
