
# Tweet Analysis (Python)

So you've [collected](https://github.com/zaman-lab/tweet-collection-py) tens of millions of tweets. Now it's time to analyze them.

## [Reproducibility Notes](NOTES.md)

## Installation

Clone this repo onto your local machine and navigate there from the command-line:

```sh
cd tweet-analysis-py/
```

Create and activate a virtual environment, using anaconda for example, if you like that kind of thing:

```sh
conda create -n tweet-analyzer-env python=3.7 # (first time only)
conda activate tweet-analyzer-env
```

Install package dependencies:

```sh
pip install -r requirements.txt # (first time only)
```

## Configuration

Create a new file in the root directory of this repo called ".env", and set your environment variables there. See the example and instructions below for more details.

```sh
# example .env file

# JOB CONFIG
#MIN_USER_ID="________"
#MAX_USER_ID="_______"
USERS_LIMIT=10000
BATCH_SIZE=20
MAX_THREADS=10

# GOOGLE APIs
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
BIGQUERY_PROJECT_NAME="tweet-collector-py"
BIGQUERY_DATASET_NAME="impeachment_development"
```

### Google API Credentials

From the Google Cloud console, enable the BigQuery API, then generate and download the corresponding service account credentials (for example into the root directory of this repo as "credentials.json") and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable accordingly.

## Usage

### Friend Collection

Fetch example data from Twitter:

```sh
python -m app.twitter_scraper
SCREEN_NAME="s2t2" python -m app.twitter_scraper
MAX_FRIENDS=5000 SCREEN_NAME="barackobama" python -m app.twitter_scraper
```

Manage and query the existing BigQuery database:

```sh
python -m app.bq_service
# DESTRUCTIVE_MIGRATIONS="true" python -m app.bq_service
```

If both of those commands work, you can collect the friend graphs, which will be stored in a new table on BigQuery called "user_friends":

```sh
python -m app.workers.friend_batch_collector
# USERS_LIMIT=100 MAX_THREADS=3 BATCH_SIZE=10 python -m app.workers.friend_batch_collector
```

### Local Analysis

If you want to download / ETL the completed "user_friends" table from BigQuery to a PostgreSQL database: create a local database called "impeachment_analysis", then set the `DATABASE_URL` environment variable. Then run the database migration script:

```sh
python -m app.models
```

After migrating the tables, you can load the data from BigQuery:

```sh
python -m app.workers.pg_pipeline
BATCH_SIZE=1000 DATASET_NAME="impeachment_production" python -m app.workers.pg_pipeline
```

### Remote File Storage

The network graph objects are so large that trying to construct them on a laptop is not feasible due to memory constraints. So we need to run the graph construction script on a larger remote server. Storage on Heroku servers is ephemeral, so we'll save the files to a Google Cloud Storage bucket instead. Configure the bucket name as an environment variable:

```sh
# .env
GCS_BUCKET_NAME="impeachment-analysis-2020"
```

In our bucket, you'll find the results of running some queries in BigQuery, so we're namespacing the storage of graph data under "storage/data", with the thinking that the "storage/data" path can mirror the local "data" and/or "test/data" dirs in this repo.

Test the connection to the storage bucket, saving some mock files there:

```sh
python -m app.gcs_service
```

### Network Graphs

Assembling network graphs directly from BigQuery data:

```sh
# incremental graph construction (uses more incremental memory):
python -m app.workers.bq_grapher
BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="true" BATCH_SIZE=1000 python app.workers.bq_grapher

# graph construction from complete edges list (uses less incremental memory):
python -m app.workers.bq_list_grapher
BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="false" python -m app.workers.bq_list_grapher
```

If those run into memory issues, run the PG Pipeline, then try assembling network graphs from PostgresSQL data:

```sh
# incremental graph construction (uses more incremental memory):
python -m app.workers.pg_grapher
USER_FRIENDS_TABLE_NAME="user_friends_10k" DRY_RUN="true" python -m app.workers.pg_grapher
USER_FRIENDS_TABLE_NAME="user_friends_10k" DRY_RUN="false" python -m app.workers.pg_grapher
USER_FRIENDS_TABLE_NAME="user_friends" DRY_RUN="false" python -m app.workers.pg_grapher
USERS_LIMIT=10000 BATCH_SIZE=1000 DRY_RUN="false" python -m app.workers.pg_grapher

# graph construction from complete edges list (uses less incremental memory):
python -m app.workers.pg_list_grapher
USERS_LIMIT=10000 BATCH_SIZE=1000 DRY_RUN="true" python -m app.workers.pg_list_grapher
BATCH_SIZE=1000 DRY_RUN="false" python -m app.workers.pg_list_grapher
```


## Testing

Run tests:

```sh
pytest
```

## [Deploying](/DEPLOYING.md)

## [License](/LICENSE.md)
