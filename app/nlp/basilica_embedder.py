import os

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

            batch_size = len(batch)
            if batch_size >= BATCH_SIZE: # FULL BATCH
                self.counter += batch_size
                self.save_batch(batch)
                self.progress_report()
                batch = []

        batch_size = len(batch)
        if batch_size >= 0: # LAST BATCH (POSSIBLY NOT FULL)
            self.counter += batch_size
            self.save_batch(batch)
            self.progress_report()
            batch = []

        self.end()

    def save_batch(self, batch):
        embeddings = list(self.bas_service.embed_tweets([row["status_text"] for row in batch], timeout=50))
        print("EMBEDDINGS COMPLETE!")

        for i, row in enumerate(batch):
            row["embedding"] = embeddings[i]
            del row["status_text"]

        self.bq_service.upload_basilica_embeddings(batch)
        print("UPLOAD COMPLETE!")


if __name__ == "__main__":

    embedder = BasilicaEmbedder()

    embedder.perform()
