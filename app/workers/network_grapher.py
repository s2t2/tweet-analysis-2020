
import time
import os
from networkx import DiGraph, write_gpickle
from google.cloud import bigquery

from app.storage_service import BigQueryService

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "follower_network.gpickle")

def process_batch(graph, batch):
    for row in batch:
        user = row["screen_name"]
        graph.add_node(user)

        for friend in row["friend_names"]:
            graph.add_node(friend)
            graph.add_edge(user, friend)

    return graph

if __name__ == "__main__":

    graph = DiGraph()

    service = BigQueryService.cautiously_initialized()
    #user_friends = service.fetch_user_friends(limit=100) # TODO: fetch in batches
    #process_batch(graph, user_friends)

    # how to fetch in batches?
    # https://cloud.google.com/bigquery/docs/running-queries#batch
    # https://cloud.google.com/bigquery/docs/paging-results

    start_at = time.perf_counter()
    counter = 1

    #rows = service.client.list_rows(f"{service.dataset_address}.user_friends") #, max_results=10
    #for row in rows:
    #    #print(row["screen_name"], row["friend_count"])
    #    counter+=1

    sql = f"""
        SELECT user_id, screen_name, friend_count, friend_names
        FROM `{service.dataset_address}.user_friends`
        -- ORDER BY screen_name;
    """
    client = service.client
    #job_config = bigquery.QueryJobConfig(priority=bigquery.QueryPriority.BATCH)
    #job_config = bigquery.QueryJobConfig(priority=bigquery.QueryPriority.BATCH, allow_large_results=True)
    job_config = bigquery.QueryJobConfig(priority=bigquery.QueryPriority.BATCH, allow_large_results=True, destination=f"{service.dataset_address}.user_friends_temp")
    job = client.query(sql, job_config=job_config)
    #job = client.get_job(job.job_id, location=job.location)  # Make an API request.
    print(job.job_id, job.state)

    for row in job:
        counter+=1

    #> google.api_core.exceptions.Forbidden: 403 GET https://bigquery.googleapis.com/bigquery/v2/projects/tweet-collector-py/queries/abc123?maxResults=0&location=US:
    #> Response too large to return. Consider setting allowLargeResults to true in your job configuration.
    #> For more information, see https://cloud.google.com/bigquery/troubleshooting-errors

    #> google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/tweet-collector-py/jobs:
    #> allow_large_results requires destination_table.




    end_at = time.perf_counter()
    duration_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {counter} USERS IN {duration_seconds} SECONDS")

    exit()









    print("NETWORK GRAPH COMPLETE!")
    print("NODES:", len(graph.nodes))
    print("EDGES:", len(graph.edges))
    print("SIZE:", graph.size())

    print("WRITING NETWORK GRAPH TO:", os.path.abspath(GPICKLE_FILEPATH))
    write_gpickle(graph, GPICKLE_FILEPATH)
