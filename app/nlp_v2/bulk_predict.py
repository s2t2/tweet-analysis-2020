import os

from pandas import DataFrame, read_csv

from app import seek_confirmation, DATA_DIR
from app.job import Job
from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))

CSV_FILEPATH = os.path.join(DATA_DIR, "nlp_v2", "all_statuses.csv")
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # whether or not to re-download if a local file already exists

def save_batch(batch, csv_filepath=CSV_FILEPATH):
    batch_df = DataFrame(batch, columns=["status_id", "status_text"])

    if os.path.isfile(csv_filepath):
        batch_df.to_csv(csv_filepath, mode="a", header=False, index=False)
    else:
        batch_df.to_csv(csv_filepath, index=False)

if __name__ == "__main__":

    bq_service = BigQueryService()
    job = Job()

    if DESTRUCTIVE or not os.path.isfile(CSV_FILEPATH):
        job.start()
        batch = []
        for row in bq_service.nlp_v2_fetch_statuses(limit=LIMIT):
            batch.append({"status_id": row["status_id"], "status_text": row["status_text"]})

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                save_batch(batch)
                batch = []
                job.progress_report()

        if len(batch) > 0:
            save_batch(batch)
            batch = []
        job.end()

    seek_confirmation()
    #exit()

    for model_name in ["logistic_regression", "multinomial_nb"]:

        storage = ModelStorage(dirpath=f"nlp_v2/models/best/{model_name}")
        tv = storage.load_vectorizer()
        clf = storage.load_model()

        print(f"DESTROY PREDICTIONS TABLE? ({model_name})")
        seek_confirmation()
        bq_service.nlp_v2_destructively_migrate_predictions_table(model_name)
        predictions_table = bq_service.nlp_v2_get_predictions_table(model_name) # API call. cache it here once.

        job.start()

        for chunk_df in read_csv(CSV_FILEPATH, chunksize=BATCH_SIZE): # FYI: this will include the last chunk even if it is not a full batch
            status_ids = chunk_df["status_id"].tolist()
            status_texts = chunk_df["status_text"].tolist()

            preds = clf.predict(tv.transform(status_texts))

            batch = [{"status_id": status_id, "prediction": pred} for status_id, pred in zip(status_ids, preds)]
            bq_service.insert_records_in_batches(predictions_table, batch)

            job.counter += len(chunk_df)
            job.progress_report()
            batch = []

        job.end()
