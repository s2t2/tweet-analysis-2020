
import os
#from pprint import pprint
#from copy import copy
from functools import lru_cache

from dotenv import load_dotenv
from detoxify import Detoxify
from pandas import DataFrame

from app import server_sleep
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
        self.model_name = model_name.lower().replace(";","") # using this model name in queries, so be super safe about SQL injection, although its not a concern right now
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
        return Detoxify(self.model_name)

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

    def count_scores(self):
        sql = f"""
            SELECT count(DISTINCT status_text_id) as text_count
            FROM `{self.scores_table_name}`
        """
        results = self.bq_service.execute_query(sql)
        return list(results)[0]["text_count"]

if __name__ == "__main__":

    scorer = ToxicityScorer()

    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    print("----------------")
    print("FETCHING TEXTS...")
    texts = list(scorer.fetch_texts())

    print("----------------")
    batches = list(split_into_batches(texts, batch_size=scorer.batch_size))
    batch_count = len(batches)
    print("ASSEMBLED", batch_count, "BATCHES OF", scorer.batch_size)

    score_columns = ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
    all_columns_in_order = ["status_text_id"] + score_columns

    for index, batch in enumerate(batches):
        print(f"... PROCESSING BATCH ({index+1} OF {batch_count})...", generate_timestamp())

        status_text_ids = [row["status_text_id"] for row in batch]
        status_texts = [row["status_text"] for row in batch]

        scores = scorer.model.predict(status_texts)
        scores["status_text_id"] = status_text_ids

        scores_df = DataFrame(scores)
        # reorder columns for BQ (or else they won't save properly):
        scores_df = scores_df.reindex(all_columns_in_order, axis="columns")
        # round scores (BUT NOT THE IDS), to reduce storage requirements:
        for column_name in score_columns:
            #scores_df[column_name] = scores_df[column_name].apply(rounded_score)
            scores_df[column_name] = scores_df[column_name].round(8)

        records = scores_df.to_dict("records")
        scorer.save_scores(records)

    print("----------------")
    print("NEW SCORES COUNT:", fmt_n(scorer.count_scores()))
    print("JOB COMPLETE :-D")

    server_sleep(seconds=10*60) # give the server a break before restarting
