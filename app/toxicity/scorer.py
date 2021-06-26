
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
TEXTS_LIMIT = os.getenv("TEXTS_LIMIT") # None by default

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
    print("BATCH SIZE:", BATCH_SIZE)
    print("TEXTS LIMIT:", TEXTS_LIMIT)

    bq_service = BigQueryService()

    scores_table_name = f"{bq_service.dataset_address}.status_toxicity_scores_{MODEL_NAME.lower()}"
    print("SCORES TABLE:", scores_table_name.upper())
    # re-migrate the table and start from scratch and hope for the best
    # ... (unless we can think of a way to query statuses not looked up - right now that is prohibitively slow due to nested arrays)
    migration_sql = f"""
        DROP TABLE IF EXISTS `{scores_table_name}`;
        CREATE TABLE IF NOT EXISTS `{scores_table_name}` (
            status_id INT64,
            identity_hate FLOAT64,
            insult FLOAT64,
            obscene FLOAT64,
            severe_toxicity FLOAT64,
            threat FLOAT64,
            toxicity FLOAT64
        );
    """
    bq_service.execute_query(migration_sql)
    scores_table = bq_service.client.get_table(scores_table_name)

    print("----------------")
    print("FETCHING TEXTS...")

    #rows = [
    #    {"status_ids": [1,2,3,4],   "status_text": "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…"},
    #    {"status_ids": [5,6,7],     "status_text": "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…"},
    #    {"status_ids": [8,9,10,11], "status_text": "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…"},
    #    {"status_ids": [12,13,14],  "status_text": "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"}
    #]

    texts_sql = f"""
        SELECT status_text_id, status_text, status_ids
        FROM `{bq_service.dataset_address}.status_texts`
    """
    if TEXTS_LIMIT:
        limit = int(TEXTS_LIMIT)
        texts_sql += f" LIMIT {limit}"

    print("----------------")
    print("SCORING TEXTS...")

    model = Detoxify(MODEL_NAME)
    print(model)

    batch = []
    text_counter = 0
    status_counter = 0
    #for row in bq_service.execute_query_in_batches(texts_sql):
    for row in bq_service.execute_query(texts_sql):
        text_counter+=1
        scores = model.predict(row["status_text"])
        scores = {
            "status_id": None, # use this order for storing in BQ (prevent append from adding this key at the end)
            "identity_hate": rounded_score(scores["identity_hate"]),
            "insult": rounded_score(scores["insult"]),
            "obscene": rounded_score(scores["obscene"]),
            "severe_toxicity": rounded_score(scores["severe_toxicity"]),
            "threat": rounded_score(scores["threat"]),
            "toxicity": rounded_score(scores["toxicity"]),
        } # round the scores

        # record per status (slower for initial storage, faster for subsequent retrieval / querying)
        for status_id in row["status_ids"]:
            record = copy(scores)
            record["status_id"] = status_id
            #print("----")
            #print(record)
            batch.append(record)
            status_counter +=1

            if len(batch) >= BATCH_SIZE:
                print("SAVING BATCH...", generate_timestamp(), " | ", fmt_n(text_counter), " | ", len(batch), " | ", fmt_n(status_counter))
                bq_service.insert_records_in_batches(scores_table, batch)
                batch = []

        #if len(batch) >= BATCH_SIZE:
        #    print("SAVING BATCH...", generate_timestamp(), " | ", fmt_n(text_counter), " | ", len(batch), " | ", fmt_n(status_counter))
        #    bq_service.insert_records_in_batches(scores_table, batch)
        #    batch = []

    if any(batch):
        print("SAVING FINAL BATCH...", generate_timestamp(), " | ", fmt_n(text_counter), " | ", len(batch), " | ", fmt_n(status_counter))
        bq_service.insert_records_in_batches(scores_table, batch)
        batch = []
