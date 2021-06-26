
import os
#from pprint import pprint
from copy import copy

from dotenv import load_dotenv
from detoxify import Detoxify

from app.bq_service import BigQueryService

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", default="original")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100"))

def rounded_score(score):
    """Rounds to eight decimal places"""
    return round(score, 8)


if __name__ == '__main__':

    print("----------------")
    print("MODEL:", MODEL_NAME.upper())

    model = Detoxify(MODEL_NAME)
    print(model)

    print("----------------")
    print("BQ SERVICE...")

    bq_service = BigQueryService()

    scores_table_name = f"{bq_service.dataset_address}.status_toxicity_scores_{MODEL_NAME.lower()}"
    print("SCORES TABLE:", scores_table_name.upper())
    scores_table = bq_service.client.get_table(scores_table_name)

    print("----------------")
    print("TEXTS...")

    rows = [
        {"status_ids": [1,2,3,4],   "status_text": "RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…"},
        {"status_ids": [5,6,7],     "status_text": "RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…"},
        {"status_ids": [8,9,10,11], "status_text": "RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…"},
        {"status_ids": [12,13,14],  "status_text": "RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…"}
    ]

    print("----------------")
    print("SCORING...")

    batch = []
    for row in rows:
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
            print("----")
            print(record)
            batch.append(record)
            #del record

        if len(batch) >= BATCH_SIZE:
            print("SAVING BATCH...")
            print(batch)

            breakpoint()
            bq_service.insert_records_in_batches(scores_table, batch)
            batch = []

    if any(batch):
        print("SAVING FINAL BATCH...")
        print(batch)

        breakpoint()
        bq_service.insert_records_in_batches(scores_table, batch)
        batch = []
