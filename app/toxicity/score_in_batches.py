
import os
#from pprint import pprint
#from copy import copy
from functools import lru_cache

from dotenv import load_dotenv
from detoxify import Detoxify
from pandas import DataFrame

from app.bq_service import BigQueryService, generate_timestamp, split_into_batches
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


class ToxicityScorer:
    def __init__(self, model_name=MODEL_NAME, limit=LIMIT, batch_size=BATCH_SIZE, bq_service=None):
        self.model_name = model_name.lower()
        self.limit = limit
        self.batch_size = batch_size
        self.bq_service = bq_service or BigQueryService()

        print("----------------")
        print("TOXICITY SCORER...")
        print("MODEL:", self.model_name.upper())
        print("LIMIT:", self.limit)
        print("BATCH SIZE:", self.batch_size)

    @property
    def scores_table_name(self):
        return f"{self.bq_service.dataset_address}.toxicity_scores_{self.model_name}"

    @property
    @lru_cache(maxsize=None)
    def scores_table(self):
        return self.bq_service.client.get_table(self.scores_table_name) # API call

    @property
    @lru_cache(maxsize=None)
    def model(self):
        return Detoxify(self.model_name) # expensive kinda

    @property
    def fetch_texts_sql(self):
        sql = f"""
            SELECT DISTINCT
                txt.status_text_id
                ,txt.status_text
            FROM `{self.bq_service.dataset_address}.status_texts` txt
            LEFT JOIN `{self.scores_table_name}` scores ON scores.status_text_id = txt.status_text_id
            WHERE scores.status_text_id IS NULL
        """
        if self.limit:
            sql += f" LIMIT {int(self.limit)} "
        return sql

    def fetch_texts(self):
        return self.bq_service.execute_query(self.fetch_texts_sql)

    def save_scores(self, records):
        self.bq_service.insert_records_in_batches(self.scores_table, records)


if __name__ == "__main__":

    scorer = ToxicityScorer()

    print("----------------")
    print("FETCHING TEXTS...")
    texts = list(scorer.fetch_texts())

    batches = list(split_into_batches(texts, batch_size=scorer.batch_size))
    print("----------------")
    print("ASSEMBLED", len(batches), "BATCHES")

    for batch in batches:

        status_text_ids = [row["status_text_id"] for row in batch]
        status_texts = [row["status_text"] for row in batch]

        scores = scorer.model.predict(status_texts)
        scores_df = DataFrame(scores)
        breakpoint()

        #record = {
        #    "status_text_id": row["status_text_id"],
        #    "identity_hate": rounded_score(scores["identity_hate"]),
        #    "insult": rounded_score(scores["insult"]),
        #    "obscene": rounded_score(scores["obscene"]),
        #    "severe_toxicity": rounded_score(scores["severe_toxicity"]),
        #    "threat": rounded_score(scores["threat"]),
        #    "toxicity": rounded_score(scores["toxicity"]),
        #} # round the scores


        #print("SAVING BATCH...", generate_timestamp(), " | ", len(batch), " | ", fmt_n(counter))
        #scorer.save_scores(records)
