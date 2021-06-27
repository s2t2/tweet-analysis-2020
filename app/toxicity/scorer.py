
import os
#from pprint import pprint
from copy import copy

from dotenv import load_dotenv
from detoxify import Detoxify

from app.bq_service import BigQueryService, generate_timestamp
from app.decorators.number_decorators import fmt_n

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", default="original")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100"))
LIMIT = os.getenv("LIMIT") # None by default

def rounded_score(np_float):
    """Converts toxicity scores to decimals that can be saved in BigQuery.
        Converts numpy floats to native floats (prevents non serializable errors).
        Rounds to eight decimal places (to save some storage space maybe).

    Params: np_float (numpy.float32)
    """
    return round(np_float.item(), 8)


if __name__ == '__main__':

    print("----------------")
    print("MODEL:", MODEL_NAME.upper())
    print("LIMIT:", LIMIT)
    print("BATCH SIZE:", BATCH_SIZE)

    bq_service = BigQueryService()

    scores_table_name = f"{bq_service.dataset_address}.toxicity_scores_{MODEL_NAME.lower()}"
    print("SCORES TABLE:", scores_table_name.upper())
    scores_table = bq_service.client.get_table(scores_table_name)

    print("----------------")
    print("FETCHING AND SCORING TEXTS...")

    model = Detoxify(MODEL_NAME)
    print(model)

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

    batch = []
    counter = 0
    #for row in bq_service.execute_query_in_batches(texts_sql):
    for row in bq_service.execute_query(sql):

        scores = model.predict(row["status_text"])

        record = {
            "status_text_id": row["status_text_id"],
            "identity_hate": rounded_score(scores["identity_hate"]),
            "insult": rounded_score(scores["insult"]),
            "obscene": rounded_score(scores["obscene"]),
            "severe_toxicity": rounded_score(scores["severe_toxicity"]),
            "threat": rounded_score(scores["threat"]),
            "toxicity": rounded_score(scores["toxicity"]),
        } # round the scores

        batch.append(record)
        counter +=1

        if len(batch) >= BATCH_SIZE:
            print("SAVING BATCH...", generate_timestamp(), " | ", fmt_n(counter))
            bq_service.insert_records_in_batches(scores_table, batch)
            batch = []

    if any(batch):
        print("SAVING FINAL BATCH...", generate_timestamp(), " | ", fmt_n(counter))
        bq_service.insert_records_in_batches(scores_table, batch)
        batch = []
