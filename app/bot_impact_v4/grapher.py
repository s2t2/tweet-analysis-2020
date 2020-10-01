
import os

from pandas import DataFrame, read_csv
from networkx import DiGraph, write_gpickle, read_gpickle

from app.decorators.number_decorators import fmt_n
from app.job import Job
from app.bq_service import BigQueryService
from app.file_storage import FileStorage

DATE = os.getenv("DATE", default="2020-01-23")
TWEET_MIN = os.getenv("TWEET_MIN")
LIMIT = os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true")

if __name__ == "__main__":

    print("------------------------")
    print("GRAPHER...")
    print("  DATE:", DATE)
    print("  TWEET_MIN:", TWEET_MIN)
    print("  LIMIT:", LIMIT)
    print("  BATCH_SIZE:", BATCH_SIZE)
    print("  DESTRUCTIVE:", DESTRUCTIVE)

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
        print(len(statuses_df))
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
        print(len(statuses_df))
        del statuses
        statuses_df.to_csv(tweets_csv_filepath)

    #
    # MAKE GRAPH

    local_graph_filepath = os.path.join(storage.local_dirpath, "graph.gpickle")
    gcs_graph_filepath = os.path.join(storage.gcs_dirpath, "graph.gpickle")

    if os.path.exists(local_graph_filepath) and not DESTRUCTIVE:
        print("LOADING GRAPH...")
        graph = read_gpickle(local_graph_filepath)
        print(type(graph), graph.number_of_nodes(), graph.number_of_edges())
    else:
        print("CREATING GRAPH...")
        graph = DiGraph()

        nodes_df = statuses_df.copy()
        nodes_df = nodes_df[["user_id", "screen_name","rate","bot"]]
        nodes_df.drop_duplicates(inplace=True)
        print(len(nodes_df))
        print(nodes_df.head())

        job.start()
        print("NODES...")
        # for each unique node in the list, add a node to the graph.
        for i, row in nodes_df.iterrows():
            graph.add_node(row["screen_name"], user_id=row["user_id"], rate=row["rate"], bot=row["bot"])

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        job.start()
        print("EDGES...")
        for row in bq_service.fetch_daily_active_tweeter_friends(date=DATE, tweet_min=TWEET_MIN, limit=LIMIT):
            graph.add_edges_from([(row["screen_name"], friend) for friend in row["friend_names"]])

            job.counter += 1
            if job.counter % BATCH_SIZE == 0:
                job.progress_report()
        job.end()

        print(type(graph), fmt_n(graph.number_of_nodes()), fmt_n(graph.number_of_edges()))
        write_gpickle(graph, local_graph_filepath)
        storage.upload_file(local_graph_filepath, gcs_graph_filepath)


    #breakpoint()
