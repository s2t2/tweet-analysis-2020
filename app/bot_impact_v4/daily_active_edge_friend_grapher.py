

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





import json
from networkx.readwrite import json_graph
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

@profile
def save_graph_as_json(graph, local_json_graph_filepath):
    print("CONVERTING GRAPH TO JSON...")
    data = json_graph.node_link_data(graph)
    print("SAVING JSON GRAPH...")
    with open(local_json_graph_filepath, "w") as json_file:
        json.dump(data, json_file, indent=4, cls=NpEncoder)





@profile
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
    if os.path.exists(tweets_csv_filepath) and not DESTRUCTIVE:
        print("LOADING TWEETS...")
        statuses_df = read_csv(tweets_csv_filepath)
    else:
        job.start()
        print("DOWNLOADING TWEETS...")
        statuses = []
        for row in bq_service.fetch_daily_active_tweeter_statuses(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT):
            statuses.append(dict(row))

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        statuses_df = DataFrame(statuses)
        del statuses
        statuses_df.to_csv(tweets_csv_filepath)
    print(fmt_n(len(statuses_df)))

    #
    # MAKE GRAPH

    local_graph_filepath = os.path.join(storage.local_dirpath, "active_edge_graph.gpickle") #CHANGED
    gcs_graph_filepath = os.path.join(storage.gcs_dirpath, "active_edge_graph.gpickle") #CHANGED

    if os.path.exists(local_graph_filepath) and not GRAPH_DESTRUCTIVE:
        graph = load_graph(local_graph_filepath)
    else:
        nodes_df = statuses_df.copy()
        nodes_df = nodes_df[["user_id", "screen_name","rate","bot"]]
        nodes_df.drop_duplicates(inplace=True)
        print(len(nodes_df))
        print(nodes_df.head())
        del statuses_df

        print("CREATING GRAPH...")
        graph = DiGraph()

        job.start()
        print("NODES...")
        # for each unique node in the list, add a node to the graph.
        for i, row in nodes_df.iterrows():
            graph.add_node(row["screen_name"], user_id=row["user_id"], rate=row["rate"], bot=row["bot"])

            job.counter += 1
            if job.counter % GRAPH_BATCH_SIZE == 0:
                job.progress_report()
        job.end()
        del nodes_df

        job.start()
        print("EDGES...")
        for row in bq_service.fetch_daily_active_edge_friends(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT): # CHANGED
            graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])

            job.counter += 1
            if job.counter % GRAPH_BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        print(type(graph), fmt_n(graph.number_of_nodes()), fmt_n(graph.number_of_edges()))
        print("SAVING GRAPH...")
        write_gpickle(graph, local_graph_filepath)
        #del graph
        #storage.upload_file(local_graph_filepath, gcs_graph_filepath)

    local_json_graph_filepath = os.path.join(storage.local_dirpath, "active_edge_graph.gpickle") #CHANGED
    gcs_json_graph_filepath = os.path.join(storage.gcs_dirpath, "active_edge_graph.gpickle")
    save_graph_as_json(graph, local_json_graph_filepath)
    #storage.upload_file(local_json_graph_filepath, gcs_json_graph_filepath)
