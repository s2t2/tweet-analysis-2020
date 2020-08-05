
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

If you need to rename any files on Google Cloud Storage, you can:

```sh
EXISTING_PATTERN="storage/data/2020-" EXISTING_DIRPATH="storage/data" NEW_DIRPATH="storage/data/archived_graphs" python -m app.gcs_file_renaming

EXISTING_DIRPATH="storage/data/archived_graphs" NEW_DIRPATH="storage/data/archived" python -m app.gcs_file_renaming
```

### [PG Pipeline](/app/pg_pipeline/README.md)

### [Friend Collection](/app/friend_collection/README.md)





## Testing

Run tests:

```sh
APP_ENV="test" pytest
```

## [Deploying](/DEPLOYING.md)

## [License](/LICENSE.md)
