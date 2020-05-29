import os
from datetime import datetime

from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud
PROJECT_NAME = os.getenv("BIGQUERY_PROJECT_NAME", default="tweet-collector-py")
DATASET_NAME = os.getenv("BIGQUERY_DATASET_NAME", default="impeachment_development") #> "_test" or "_production"

# CONNECT TO DATABASE

client = bigquery.Client()

# CREATING TABLES

dataset_address = f"{PROJECT_NAME}.{DATASET_NAME}"
table_address = f"{dataset_address}.my_table_123"

sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_address}` (
        user_id STRING,
        screen_name STRING,
        friend_count INT64,
        friend_names ARRAY<STRING>
    );
"""
client.query(sql)

# INSERTS
#dataset_ref = client.dataset(DATASET_NAME) # WARNING: PendingDeprecationWarning: Client.dataset is deprecated and will be removed in a future version. Use a string like 'my_project.my_dataset' or a cloud.google.bigquery.DatasetReference object, instead.
#table_ref = dataset_ref.table("my_table")
#my_table = client.get_table(table_ref) # an API call (caches results for subsequent inserts)

my_table = client.get_table(table_address) # an API call (caches results for subsequent inserts)

rows_to_insert = [
    ["id1", "screen_name1", 2, ["friend1", "friend2"]],
    ["id2", "screen_name2", 2, ["friend3", "friend4"]],
]
errors = client.insert_rows(my_table, rows_to_insert)
print(errors)

# QUERYING

sql = f"SELECT * FROM `{table_address}`;"
job = client.query(sql)
results = list(job.result())
for row in results:
    print(row)
    print("---")

# FETCHING IN BATCHES

sql = f"SELECT * FROM `{table_address}`"

job_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S') # unique for each job
job_destination_address = f"{dataset_address}.job_{job_name}"
job_config = bigquery.QueryJobConfig(
    priority=bigquery.QueryPriority.BATCH,
    allow_large_results=True,
    destination=job_destination_address
)

job = client.query(sql, job_config=job_config)
print("JOB (FETCH USER FRIENDS):", type(job), job.job_id, job.state, job.location)
for row in job:
    print(row)
