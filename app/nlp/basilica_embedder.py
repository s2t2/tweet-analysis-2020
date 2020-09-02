import os

from app.job import Job
from app.bq_service import BigQueryService
from app.basilica_service import BasilicaService

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

        print("FETCHING STATUSES IN BATCHES...")
        self.batch = []
        for row in self.bq_service.fetch_basilica_embedless_partitioned_statuses(selections="status_id, status_text", limit=LIMIT, in_batches=True):
            self.batch.append(dict(row))

            batch_size = len(self.batch)
            if batch_size >= BATCH_SIZE: # FULL BATCH
                self.counter += batch_size
                self.save_batch(self.batch)
                self.batch = []
                self.progress_report()

        batch_size = len(self.batch)
        if batch_size >= 0: # LAST BATCH (POSSIBLY NOT FULL)
            self.counter += batch_size
            self.save_batch(self.batch)
            self.batch = []
            self.progress_report()

        self.end()

    def save_batch(self, batch):
        embeddings = list(self.bas_service.embed_tweets([row["status_text"] for row in batch]))

        for i, row in enumerate(batch):
            row["embedding"] = embeddings[i]
            del row["status_text"]

        self.bq_service.upload_basilica_embeddings(batch)


if __name__ == "__main__":

    embedder = BasilicaEmbedder()

    embedder.perform()
