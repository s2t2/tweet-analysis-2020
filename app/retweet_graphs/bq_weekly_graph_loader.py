
import os

from app import DATA_DIR
from app.graph_storage_service import GraphStorageService
from app.retweet_graphs.bq_weekly_grapher import WEEK_ID

if __name__ == "__main__":


    #grapher = BigQueryWeeklyRetweetGrapher()

    storage_service = GraphStorageService(
        local_dirpath = os.path.join(DATA_DIR, "graphs", "weekly", WEEK_ID),
        gcs_dirpath = os.path.join("storage", "data", "graphs", "weekly", WEEK_ID)
    )

    storage_service.graph = storage_service.load_graph() # will print a memory profile...

    storage_service.report() # will print graph size
