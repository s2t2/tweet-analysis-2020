

import os

from pandas import DataFrame, read_csv
from networkx import DiGraph, write_gpickle, read_gpickle
from memory_profiler import profile

from app.decorators.number_decorators import fmt_n
from app.job import Job
from app.bq_service import BigQueryService
from app.file_storage import FileStorage

DATE = os.getenv("DATE", default="2020-01-23")
TWEET_MIN = int(os.getenv("TWEET_MIN", default="1")) # CHANGED

LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true")

#GRAPH_LIMIT = os.getenv("GRAPH_LIMIT")
GRAPH_BATCH_SIZE = int(os.getenv("GRAPH_BATCH_SIZE", default="10000"))
GRAPH_DESTRUCTIVE = (os.getenv("GRAPH_DESTRUCTIVE", default="false") == "true")

#@profile
def load_graph(local_graph_filepath):
    print("LOADING GRAPH...")
    graph = read_gpickle(local_graph_filepath)
    print(type(graph), fmt_n(graph.number_of_nodes()), fmt_n(graph.number_of_edges()))
    return graph

if __name__ == "__main__":

    print("------------------------")
    print("GRAPHER...")
    print("  DATE:", DATE)
    print("  TWEET_MIN:", TWEET_MIN)

    print("  LIMIT:", LIMIT)
    print("  BATCH_SIZE:", BATCH_SIZE)
    print("  DESTRUCTIVE:", DESTRUCTIVE)

    #print("  GRAPH_LIMIT:", GRAPH_LIMIT)
    print("  GRAPH_BATCH_SIZE:", GRAPH_BATCH_SIZE)
    print("  GRAPH_DESTRUCTIVE:", GRAPH_DESTRUCTIVE)

    print("------------------------")
    storage = FileStorage(dirpath=f"daily_active_friend_graphs_v4/{DATE}/tweet_min/{TWEET_MIN}")
    tweets_csv_filepath = os.path.join(storage.local_dirpath, "tweets.csv")

    bq_service = BigQueryService()
    job = Job()

    #
    # LOAD TWEETS
    # tweet_id, text, screen_name, bot, created_at

    # TODO: de-dup RTs so the model will only train/test on a single RT status text (PREVENT OVERFITTING)


    if os.path.exists(tweets_csv_filepath) and not DESTRUCTIVE:
        print("LOADING TWEETS...")
        statuses_df = read_csv(tweets_csv_filepath)
    else:
        job.start()
        print("DOWNLOADING TWEETS...")
        statuses = []
        for row in bq_service.fetch_daily_active_tweeter_statuses_for_model_training(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT):
            statuses.append(dict(row))

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        statuses_df = DataFrame(statuses)
        del statuses
        statuses_df.to_csv(tweets_csv_filepath)
    print("STATUSES:", fmt_n(len(statuses_df)))

    #
    # MAKE GRAPH

    local_nodes_csv_filepath = os.path.join(storage.local_dirpath, "active_nodes.csv")
    local_graph_csv_filepath = os.path.join(storage.local_dirpath, "active_edge_graph.csv") #CHANGED
    if os.path.exists(local_nodes_csv_filepath) and os.path.exists(local_graph_csv_filepath) and not GRAPH_DESTRUCTIVE:
        nodes_df = read_csv(local_nodes_csv_filepath)
        graph_df = read_csv(local_graph_csv_filepath)
    else:
        nodes_df = statuses_df.copy()
        nodes_df = nodes_df[["user_id", "screen_name","rate","bot"]]
        nodes_df.drop_duplicates(inplace=True)
        print("NODES:", fmt_n(len(nodes_df)))
        print(nodes_df.head())
        nodes_df.to_csv(local_nodes_csv_filepath)

        del statuses_df

        job.start()
        print("ACTIVE EDGES...")
        active_edges = []
        for row in bq_service.fetch_daily_active_edge_friends_for_csv(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT): # CHANGED
            active_edges.append(dict(row))

            job.counter += 1
            if job.counter % GRAPH_BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        graph_df = DataFrame(active_edges)
        print(fmt_n(len(graph_df)))
        print(graph_df.head())
        print("SAVING GRAPH TO CSV...")
        graph_df.to_csv(local_graph_csv_filepath)

        # todo: upload straight to google drive
