
import os
from threading import current_thread, BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor, as_completed # see: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

from dotenv import load_dotenv
from detoxify import Detoxify

from app.bq_service import BigQueryService, generate_timestamp, split_into_batches
from app.decorators.number_decorators import fmt_n
from app.toxicity.scorer import rounded_score, MODEL_NAME, LIMIT, BATCH_SIZE

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=10)) # the max number of threads to use, for concurrent processing

def process_batch_of_texts(bq_service, batch_of_texts, model, scores_table):
    print("PROCESSING BATCH OF TEXTS...", generate_timestamp(), " | ", len(batch_of_texts), " | ", current_thread().name)
    batch_of_scores = []
    for text in batch_of_texts:
        batch_of_scores.append(process_text(model, text))
    #bq_service.insert_records_in_batches(scores_table, batch_of_scores)


def process_text(model, row):
    scores = model.predict(row["status_text"])
    return {
        "status_text_id": row["status_text_id"],
        # round the scores
        "identity_hate": rounded_score(scores["identity_hate"]),
        "insult": rounded_score(scores["insult"]),
        "obscene": rounded_score(scores["obscene"]),
        "severe_toxicity": rounded_score(scores["severe_toxicity"]),
        "threat": rounded_score(scores["threat"]),
        "toxicity": rounded_score(scores["toxicity"]),
    }


if __name__ == '__main__':

    print("----------------")
    print("MODEL:", MODEL_NAME.upper())
    print("LIMIT:", LIMIT)
    print("BATCH SIZE:", BATCH_SIZE)
    print("MAX THREADS:", MAX_THREADS)

    model = Detoxify(MODEL_NAME)

    bq_service = BigQueryService()
    scores_table_name = f"{bq_service.dataset_address}.toxicity_scores_{MODEL_NAME.lower()}"
    scores_table = bq_service.client.get_table(scores_table_name)

    sql = f"""
        SELECT DISTINCT
            txt.status_text_id
            ,txt.status_text
        FROM `{bq_service.dataset_address}.status_texts` txt
        LEFT JOIN `{scores_table_name}` scores ON scores.status_text_id = txt.status_text_id
        WHERE scores.status_text_id IS NULL
    """
    if LIMIT:
        sql += f" LIMIT {int(LIMIT)} "

    texts = list(bq_service.execute_query(sql))
    print("FETCHED", len(texts), "TEXTS")
    batches_of_texts = list(split_into_batches(texts))
    print("ASSEMBLED", len(batches_of_texts), "BATCHES OF TEXTS")

    print("-------------")
    print("SCORING TEXTS IN BATCHES...")

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="THREAD") as executor:

        futures = [
            executor.submit(process_batch_of_texts, bq_service, batch_of_texts, model, scores_table)
            for batch_of_texts in batches_of_texts
        ]

        print("FUTURE RESULTS", len(futures))
        for index, future in enumerate(as_completed(futures)):
            future.result()
