
# Tweet Analysis (Python)

So you've [collected](https://github.com/zaman-lab/tweet-collection-py) tens of millions of tweets about a given topic and stored them in Google BigQuery (see [Dataset Exploration Notes](/notes/dataset-exploration.md)). Now it's time to analyze them.

This research project builds upon the work of Tauhid Zaman, Nicolas Guenon Des Mesnards, et. al., as described by the paper: ["Detecting Bots and Assessing Their Impact in Social Networks"](https://arxiv.org/abs/1810.12398).

Dependencies:

  + Python 3.7
  + PostgreSQL

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

## Setup

### Google BigQuery and API Credentials

The tweets are stored in a Google BigQuery database, so we'll need BigQuery credentials to access the data. From the [Google Cloud console](https://console.cloud.google.com/), enable the BigQuery API, then generate and download the corresponding service account credentials. Move them into the root directory of this repo as "credentials.json", and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable accordingly (see environment variable setup below).

#### Google Cloud Storage

The network graph objects are so large that trying to construct them on a laptop is not feasible due to memory constraints. So we need to run various graph construction scripts on a larger remote server. Storage on Heroku servers is ephemeral, so we'll save the files to a Google Cloud Storage bucket instead. Create a new bucket or gain access to an existing bucket, and set the `GCS_BUCKET_NAME` environment variable accordingly (see environment variable setup below).

FYI: in the bucket, there will also exist some temporary tables used by BigQuery during batch job performances, so we're namespacing the storage of graph data under "storage/data", with the thinking that the "storage/data" path can mirror the local "data" and/or "test/data" dirs in this repo.

### Local Database Setup

We'll be downloading some of the data from BigQuery to a local database, for faster processing. So first create a local PostgreSQL database called "impeachment_analysis", then set the `DATABASE_URL` environment variable accordingly (see environment variable setup below).

### Environment Variables

Create a new file in the root directory of this repo called ".env", and set your environment variables there, as necessary:

```sh
# example .env file

#
# GOOGLE APIs
#

GOOGLE_APPLICATION_CREDENTIALS="/path/to/tweet-analysis-py/credentials.json"
BIGQUERY_PROJECT_NAME="tweet-collector-py"
BIGQUERY_DATASET_NAME="impeachment_development"
# GCS_BUCKET_NAME="impeachment-analysis-2020"

#
# LOCAL PG DATABASE
#

# DATABASE_URL="postgresql://USERNAME:PASSWORD@localhost/impeachment_analysis"

#
# EMAIL
#

SENDGRID_API_KEY="__________"
MY_EMAIL_ADDRESS="hello@example.com"

#
# JOB CONFIG VARS
#

# MIN_USER_ID="________"
# MAX_USER_ID="_______"
# USERS_LIMIT=10000
# BATCH_SIZE=20
# MAX_THREADS=10
```

## Usage

Testing the Google BigQuery connection:

```sh
python -m app.bq_service
# DESTRUCTIVE_MIGRATIONS="true" python -m app.bq_service
```

Testing the Google Cloud Storage connection, saving some mock files in the specified bucket:

```sh
python -m app.gcs_service
```

Testing the local PostgreSQL database connection:

```sh
python -m app.models
```

### Friend Collection

> See: [Friend Collection Notes](/notes/friend-collection.md).

Testing the Twitter scraper (doesn't need credentials):

```sh
python -m app.friend_collection.twitter_scraper
# SCREEN_NAME="s2t2" python -m app.friend_collection.twitter_scraper
# MAX_FRIENDS=5000 SCREEN_NAME="barackobama" python -m app.friend_collection.twitter_scraper
```

Fetching user friends (people they follow), and storing them in the "user_friends" table on BigQuery:

```sh
python -m app.app.friend_collection_in_batches
# USERS_LIMIT=100 MAX_THREADS=3 BATCH_SIZE=10 python -m app.app.friend_collection_in_batches
```

### Local Database Migration

Downloading the "user_friends" table:

```sh
#python -m app.workers.pg_pipeline_user_friends
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=1000 python -m app.workers.pg_pipeline_user_friends
```

Downloading the "user_details" table:

```sh
#BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true USERS_LIMIT=1000 BATCH_SIZE=300 python -m app.workers.pg_pipeline_user_details
BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true BATCH_SIZE=2500 python -m app.workers.pg_pipeline_user_details
```

Downloading the "retweeter_details" table:

```sh

# BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true USERS_LIMIT=1000 BATCH_SIZE=300 python -m app.workers.pg_pipeline_retweeter_details
BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true BATCH_SIZE=2500 python -m app.workers.pg_pipeline_retweeter_details
```

### Friend Graphs

> See: [Friend Graph Notes](/notes/friend-graphs.md).

In order to analyze Twitter user network graphs, we'll attempt to construct a `networkx` Graph object and make use of some of its built-in analysis capabilities.

When assembling this network graph object, one option is to stream the user data directly from BigQuery:

```sh
# incremental graph construction (uses more incremental memory):
python -m app.workers.bq_grapher
BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="true" BATCH_SIZE=1000 python app.workers.bq_grapher

# graph construction from complete edges list (uses less incremental memory):
python -m app.workers.bq_list_grapher
BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="false" python -m app.workers.bq_list_grapher
```

However, depending on the size of the graph, that approach might run into memory errors. So another option is to query the data from the local PostgreSQL database. First, ensure you've setup and populated a remote Heroku PostgreSQL database using the "Local Database Setup" and "Local Database Migration" instructions above. After the database is ready, you can try to assemble the network graph object from the PostgreSQL data:

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
USERS_LIMIT=100000 BATCH_SIZE=1000 DRY_RUN="false" python -m app.workers.pg_list_grapher
```

> NOTE: you might be unable to create graph objects to cover your entire user dataset, so just make the largest possible given the memory constraints of the computers and servers available to you by trying to get the `USERS_LIMIT` as large as possible.

The graphs are very large, so how about we create a few different smaller topic-specific graphs:

```sh
# assemble right-leaning conversation graph:
BIGQUERY_DATASET_NAME="impeachment_production" USERS_LIMIT=1000 BATCH_SIZE=100 TOPIC="#MAGA" python -m app.workers.bq_custom_grapher

# assemble left-leaning conversation graph:
BIGQUERY_DATASET_NAME="impeachment_production" USERS_LIMIT=1000 BATCH_SIZE=100 TOPIC="#ImpeachAndConvict" python -m app.workers.bq_custom_grapher
```

### Retweet Graphs

> See: [Retweet Graph Notes](/notes/retweet-graphs.md).

Construct retweet graphs:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 TOPIC="impeach" python -m app.workers.bq_retweet_grapher

BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 TOPIC="#MAGA" python -m app.workers.bq_retweet_grapher

BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 "#ImpeachAndConvict" python -m app.workers.bq_retweet_grapher
```

Observe the resulting job identifier (`JOB_ID`), and verify the graph and other artifacts are saved to local storage and/or Google Cloud Storage.

Once you have created a retweet graph, note its `JOB_ID`, and see how much memory it takes to load a given graph:

```py
# right-leaning conversation graph
JOB_ID="2020-06-07-2049" STORAGE_MODE="local" python -m app.graph_analyzer
JOB_ID="2020-06-07-2049" STORAGE_MODE="remote" python -m app.graph_analyzer

# left-leaning conversation graph
JOB_ID="2020-06-07-2056" STORAGE_MODE="local" python -m app.graph_analyzer
JOB_ID="2020-06-07-2056" STORAGE_MODE="remote" python -m app.graph_analyzer

# neutral conversation retweet graph
JOB_ID="2020-06-15-2141" STORAGE_MODE="local" python -m app.graph_analyzer
```


### Bot Classification

Once you have created a retweet graph, note its `JOB_ID`, then compute bot probabilities for each node:

```sh
# JOB_ID="2020-06-15-2141" python -m app.botcode_v2.classifier
JOB_ID="2020-06-15-2141" DRY_RUN="false" python -m app.botcode_v2.classifier
```

This will download the graph from Google Cloud Storage, if necessary, into its local storage directory, and then save a CSV file of bot probabilities in that directory as well.


















































### KS Tests

#### Retweeter Age Distribution By Topic

Compare the distribution of user creation dates for those retweeting about a given topic, vs those not retweeting about that topic:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" TOPIC="#ImpeachAndConvict" python -m app.ks_test.topic_analyzer
```

#### Retweeter Age Distribution By Topic Pair

Compare the distribution of user creation dates for those retweeting exclusively about one of two different topics:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" X_TOPIC="#ImpeachAndConvict" Y_TOPIC="#MAGA" python -m app.ks_test.topic_pair_analyzer
```


## Testing

Run tests:

```sh
pytest
```

## [Deploying](/DEPLOYING.md)

## [License](/LICENSE.md)
