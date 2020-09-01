import os

from app.bq_service import BigQueryService
from app.basilica_service import BasilicaService

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="1_000"))

if __name__ == "__main__":

    bas_service = BasilicaService()

    print("LIMIT:", LIMIT)
    print("BATCH SIZE:", BATCH_SIZE)

    bq_service = BigQueryService()

    # destructively create embeddings_table
    # ... manually (see README.md)

    # loop through tweet statuses in batches of 1000, and:
    #   ask for embeddings from basilica
    #   then insert the embeddings into the embeddings table with rows like (status_id, embeddings)

    batch = []
    #ids = [], texts = [], embeddings = []
    for row in bq_service.fetch_statuses_in_batches(selections="status_id, status_text", limit=LIMIT):
        batch.append(dict(row))

        batch_size = len(batch)
        if batch_size >= BATCH_SIZE: # when batch is full
            print("FETCHING {batch_size} EMBEDDINGS...")
            embeddings = list(bas_service.embed_tweets_in_batches([row["status_text"] for row in batch]))

            for i, row in enumerate(batch):
                row["embedding"] = embeddings[i]

            print(f"UPLOADING BATCH OF {batch_size}...")
            #bq_service.upload_basilica_embeddings(batch)
            print(batch[0])
            batch = []

    if batch_size >= 0: # when batch is last
        print(f"SAVING FINAL BATCH OF {batch_size}...")
        #bq_service.upload_basilica_embeddings(batch)
