


import os
from functools import lru_cache
#from pprint import pprint

from dotenv import load_dotenv

from app import server_sleep, seek_confirmation
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService, generate_timestamp, split_into_batches
from app.toxicity.model_manager import ModelManager, CHECKPOINT_NAME

load_dotenv()

LIMIT = int(os.getenv("LIMIT", default="25_000")) # number of records to fetch from bq at a time
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000")) # number of texts to score at a time (ideal is 1K, see README)

class ToxicityScorer:
    def __init__(self, limit=LIMIT, batch_size=BATCH_SIZE, bq_service=None, model_manager=None):
        self.limit = limit
        self.batch_size = batch_size
        self.bq_service = bq_service or BigQueryService()
        self.mgr = model_manager or ModelManager()

        print("----------------")
        print("TOXICITY SCORER...")
        print("  MODEL CHECKPOINT:", self.mgr.checkpoint_name.upper(), self.mgr.checkpoint_url)
        print("  SCORES TABLE NAME:", self.scores_table_name)
        print("  LIMIT:", fmt_n(self.limit))
        print("  BATCH SIZE:", fmt_n(self.batch_size))

        seek_confirmation()

        #self.mgr.load_model_state()

    def perform(self):
        print("----------------")
        print(f"FETCHING TEXTS...")
        print(f"SCORING TEXTS IN BATCHES...")

        batch = []
        counter = 0
        for row in self.fetch_texts():
            batch.append(row)

            if len(batch) >= self.batch_size:
                counter += len(batch)
                print("  ", generate_timestamp(), "|", fmt_n(counter))

                self.process_batch(batch)
                batch = []

        # process final (potentially incomplete) batch
        if any(batch):
            counter += len(batch)
            print("  ", generate_timestamp(), "|", fmt_n(counter))

            self.process_batch(batch)
            batch = []

    def fetch_texts(self):
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
        return self.bq_service.execute_query(sql) # API call

    def process_batch(self, batch):
        texts = []
        text_ids = []
        for text_row in batch:
            texts.append(text_row["status_text"])
            text_ids.append(text_row["status_text_id"])

        results = self.mgr.predict_scores(texts)

        score_rows = []
        for text_id, result in zip(text_ids, results):
            score_row = result.round(8).tolist()
            score_row.insert(0, text_id) # adds the text_id to the front of the list (proper column order -- see table definition)
            score_rows.append(score_row)

        self.save_scores(score_rows)

    def save_scores(self, values):
        """Params : values (list of lists corresponding with the proper column order)"""
        return self.bq_service.client.insert_rows(self.scores_table, values) # API call

    @property
    @lru_cache(maxsize=None)
    def scores_table(self):
        return self.bq_service.client.get_table(self.scores_table_name) # API call

    @property
    @lru_cache(maxsize=None)
    def scores_table_name(self):
        model_name = self.mgr.checkpoint_name.lower().replace("-","_").replace(";","") # using this model name in queries, so be super safe about SQL injection, although its not a concern right now
        return f"{self.bq_service.dataset_address}.toxicity_scores_{model_name}_ckpt"

    def count_scores(self):
        sql = f"""
            SELECT count(DISTINCT status_text_id) as scored_text_count
            FROM `{self.scores_table_name}`
        """
        results = self.bq_service.execute_query(sql) # API call
        return list(results)[0]["scored_text_count"]








if __name__ == "__main__":

    scorer = ToxicityScorer()

    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    scorer.mgr.load_model_state()
    scorer.perform()

    print("----------------")
    print("JOB COMPLETE!")
    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    server_sleep(seconds=10*60) # give the server a break before restarting
