import os

from app.bq_service import BigQueryService
from app.basilica_service import BasilicaService

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000"))

class BasilicaEmbedder:
    def __init__(self):
        self.bq_service = BigQueryService()
        self.bas_service = BasilicaService()

        print("-------------------")
        print("BASILICA EMBEDDER...")
        print("  LIMIT:", LIMIT)
        print("  BATCH SIZE:", BATCH_SIZE)

        #self.fetch_in_batches = self.bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT)

    def destructively_migrate(self):
        self.bq_service.destructively_migrate_basilica_embeddings_table()


    def save_batch(self, batch):
        print(f"PROCESSING BATCH OF {batch_size}...")

        embeddings = list(self.bas_service.embed_tweets_in_batches([row["status_text"] for row in batch]))

        for i, row in enumerate(batch):
            row["embedding"] = embeddings[i]
            del row["status_text"]

        self.bq_service.upload_basilica_embeddings(batch)


if __name__ == "__main__":


    embedder = BasilicaEmbedder()

    embedder.destructively_migrate()

    batch = []
    for row in embedder.bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT):
        batch.append(dict(row))

        batch_size = len(batch)
        if batch_size >= BATCH_SIZE: # when batch is full
            embedder.save_batch(batch)
            batch = []

    if batch_size >= 0: # when batch is last
        embedder.save_batch(batch)
        batch = []
