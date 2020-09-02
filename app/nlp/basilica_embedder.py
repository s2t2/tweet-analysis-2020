import os

from app.decorators.datetime_decorators import logstamp
from app.job import Job
from app.bq_service import BigQueryService
from app.basilica_service import BasilicaService

MIN_VAL = float(os.getenv("MIN_VAL", default="0.0"))
MAX_VAL = float(os.getenv("MAX_VAL", default="1.0"))
LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000"))

class BasilicaEmbedder(Job):
    def __init__(self):
        self.bq_service = BigQueryService()
        self.bas_service = BasilicaService()

        print("-------------------")
        print("BASILICA EMBEDDER...")
        print("  LIMIT:", LIMIT)
        print("  BATCH SIZE:", BATCH_SIZE)

        Job.__init__(self)

    def perform(self):
        self.start()

        #self.bq_service.destructively_migrate_basilica_embeddings_table()

        batch = []
        fetch_in_batches = not (LIMIT and int(LIMIT) <= 200_000) # straight query if a small limit is set
        for row in self.bq_service.fetch_basilica_embedless_partitioned_statuses(min_val=MIN_VAL, max_val=MAX_VAL, limit=LIMIT, in_batches=fetch_in_batches):
            batch.append(dict(row))

            if len(batch) >= BATCH_SIZE: # FULL BATCH
                self.counter += self.save_batch(batch)
                self.progress_report()
                batch = []

        if len(batch) >= 0: # LAST BATCH (POSSIBLY NOT FULL)
            self.counter += self.save_batch(batch)
            self.progress_report()
            batch = []

        self.end()

    def save_batch(self, batch):
        try:
            embeddings = list(self.bas_service.embed_tweets([row["status_text"] for row in batch]))
            print(logstamp(), "EMBEDDINGS COMPLETE!")
        except Exception as err:
            print(logstamp(), "OOPS", err, "SKIPPING...")
            return 0

        for i, row in enumerate(batch):
            row["embedding"] = embeddings[i]
            del row["status_text"]

        self.bq_service.upload_basilica_embeddings(batch)
        print("UPLOAD COMPLETE!")
        return len(batch)


if __name__ == "__main__":

    embedder = BasilicaEmbedder()

    embedder.perform()
