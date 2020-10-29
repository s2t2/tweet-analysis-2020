

import os
from pandas import read_csv, DataFrame

from app.file_storage import FileStorage
from app.bq_service import BigQueryService
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # for development purposes
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="10_000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # whether or not to re-download if a local file already exists

if __name__ == "__main__":

    bq_service = BigQueryService()
    job = Job()

    storage = FileStorage(dirpath=f"nodes_with_active_edges_v7")

    nodes_csv_filepath = os.path.join(storage.local_dirpath, "sn_nodes.csv")
    if os.path.exists(nodes_csv_filepath) and not DESTRUCTIVE:
        print("LOADING SN NODES...")
        nodes_df = read_csv(nodes_csv_filepath)
    else:
        job.start()
        print("DOWNLOADING SN NODES...")
        records = []
        for row in bq_service.fetch_sn_nodes_with_active_edges_v7(limit=LIMIT):
            records.append(dict(row))
            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()
        nodes_df = DataFrame(records)
        nodes_df.to_csv(nodes_csv_filepath, index=False)
    print("SN NODES:", fmt_n(len(nodes_df)))

    #nodes_csv_filepath = os.path.join(storage.local_dirpath, "id_nodes.csv")
    #if os.path.exists(nodes_csv_filepath) and not DESTRUCTIVE:
    #    print("LOADING NODES...")
    #    nodes_df = read_csv(nodes_csv_filepath)
    #else:
    #    job.start()
    #    print("DOWNLOADING NODES...")
    #    records = []
    #    for row in bq_service.fetch_nodes_with_active_edges_v7_sn(limit=LIMIT):
    #        records.append(dict(row))
    #        job.counter += 1
    #        if job.counter % BATCH_SIZE == 0:
    #            job.progress_report()
    #    job.end()
    #    nodes_df = DataFrame(records)
    #    nodes_df.to_csv(nodes_csv_filepath, index=False)

    print("ID NODES:", fmt_n(len(nodes_df)))
