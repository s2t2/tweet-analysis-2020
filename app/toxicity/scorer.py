
import os
from functools import lru_cache
#from pprint import pprint

from dotenv import load_dotenv
from detoxify import Detoxify
from pandas import DataFrame

from app import server_sleep
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService, generate_timestamp, split_into_batches

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", default="original") # "original" or "unbiased" (see README)
LIMIT = int(os.getenv("LIMIT", default="25_000")) # number of records to fetch from bq at a time
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000")) # number of texts to score at a time (ideal is 1K, see README)

class ToxicityScorer:
    def __init__(self, model_name=MODEL_NAME, limit=LIMIT, batch_size=BATCH_SIZE, bq_service=None):
        self.model_name = model_name.lower().replace(";","") # using this model name in queries, so be super safe about SQL injection, although its not a concern right now
        self.limit = limit
        self.batch_size = batch_size
        self.bq_service = bq_service or BigQueryService()

        print("----------------")
        print("TOXICITY SCORER...")
        print("  MODEL:", self.model_name.upper())
        print("  LIMIT:", fmt_n(self.limit))
        print("  BATCH SIZE:", fmt_n(self.batch_size))

    @property
    @lru_cache(maxsize=None)
    def scores_table_name(self):
        return f"{self.bq_service.dataset_address}.toxicity_scores_{self.model_name}"

    def count_scores(self):
        sql = f"""
            SELECT count(DISTINCT status_text_id) as text_count
            FROM `{self.scores_table_name}`
        """
        results = self.bq_service.execute_query(sql) # API call
        return list(results)[0]["text_count"]

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

    @property
    @lru_cache(maxsize=None)
    def model(self):
        return Detoxify(self.model_name)

    @property
    @lru_cache(maxsize=None)
    def scores_table_colnames(self):
        """Returns the column names in the proper order."""
        return ["status_text_id"] + self.model.class_names

    #def save_score_records(self, records):
    #    self.bq_service.insert_records_in_batches(self.scores_table, records) # API call

    def save_scores(self, values):
        """Params : values (list of lists corresponding with the proper column order)"""
        return self.bq_service.client.insert_rows(self.scores_table, values) # API call

    @property
    @lru_cache(maxsize=None)
    def scores_table(self):
        return self.bq_service.client.get_table(self.scores_table_name) # API call

    def process_batch(self, batch):
        scores = self.model.predict([row["status_text"] for row in batch])
        scores["status_text_id"] = [row["status_text_id"] for row in batch]

        scores_df = DataFrame(scores)
        # reorder columns for BQ (so they save properly):
        scores_df = scores_df.reindex(self.scores_table_colnames, axis="columns")
        # round scores, to reduce storage requirements:
        for scores_col in self.model.class_names:
            scores_df[scores_col] = scores_df[scores_col].round(8)
        #self.save_score_records(scores_df.to_dict("records"))
        self.save_scores(scores_df.to_dict(orient="split")["data"])

    def perform(self):
        print("----------------")
        print(f"FETCHING TEXTS...")
        rows = list(self.fetch_texts())

        print(f"ASSEMBLING BATCHES...")
        batches = list(split_into_batches(rows, batch_size=self.batch_size))

        print(f"SCORING TEXTS IN BATCHES...")
        counter = 0
        for index, batch in enumerate(batches):
            counter += len(batch)
            print("  ", generate_timestamp(), f"BATCH {index+1}", f"| {fmt_n(counter)}")
            self.process_batch(batch)

    def perform_better(self):
        print("----------------")
        print(f"FETCHING TEXTS...")
        print(f"SCORING TEXTS IN BATCHES...")

        batch = []
        counter = 0
        for row in self.fetch_texts():
            batch.append(row)

            if len(batch) >= self.batch_size:
                counter+=len(batch)
                print("  ", generate_timestamp(), "|", fmt_n(counter))
                self.process_batch(batch)
                batch = []



if __name__ == "__main__":

    scorer = ToxicityScorer()

    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    #scorer.perform()
    scorer.perform_better()
    #scorer.perform_better_timed()
    #duration_seconds = scorer.perform_better_timed()
    #items_per_second = round(scorer.limit / duration_seconds, 2)
    #print(f"PROCESSED {fmt_n(scorer.limit)} ITEMS IN {duration_seconds} SECONDS ({items_per_second} ITEMS / SECOND)")

    print("----------------")
    print("JOB COMPLETE!")

    print("----------------")
    print("SCORES COUNT:", fmt_n(scorer.count_scores()))

    server_sleep(seconds=10*60) # give the server a break before restarting
