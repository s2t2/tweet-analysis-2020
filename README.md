
# Tweet Analysis (Python)

So you've [collected](https://github.com/zaman-lab/tweet-collection-py) tens of millions of tweets about a given topic and stored them in Google BigQuery. Now it's time to analyze them.

This project builds upon the research of Tauhid Zaman, Nicolas Guenon Des Mesnards, et. al., as described by the paper: ["Detecting Bots and Assessing Their Impact in Social Networks"](https://arxiv.org/abs/1810.12398).

## Table of Contents

Version 1 (works in progress, investigations, archive):

  + [Tweet Collection v1](/app/tweet_collection/README.md)
  + [Friend Collection v1](/app/friend_collection/README.md)
    + [Friend Graphs v1](/app/friend_graphs/README.md)
  + [PG Pipeline](/app/pg_pipeline/README.md) (Local Database Migrations)
  + [Retweet Graphs v1](/app/retweet_graphs/README.md)
    + [Bot Classification v1](/app/botcode)
    + [Bot Classification v2](/app/retweet_graphs/README.md#Bot-Classification)
    + [KS Tests v1](/app/retweet_graphs/README.md#KS-Tests)
  + [Retweet Graphs v2](/app/retweet_graphs_v2/README.md)

Version 2 (current, stable, mature):

  + [Tweet Collection v2](/app/tweet_collection_v2/README.md)


## Installation

Dependencies:

  + Git
  + Python 3.7
  + PostgreSQL

Clone this repo onto your local machine and navigate there from the command-line:

```sh
cd tweet-analysis-py/
```

Create and activate a virtual environment, using anaconda for example, if you like that kind of thing:

```sh
conda create -n tweet-analyzer-env python=3.7
conda activate tweet-analyzer-env
```

Install package dependencies:

```sh
pip install -r requirements.txt
```

## Setup

### Twitter API Credentials

Obtain credentials which provide read access to the Twitter API. Set the environment variables `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, and `TWITTER_ACCESS_TOKEN_SECRET` accordingly (see environment variable setup below).

### Google BigQuery and API Credentials

The tweets are stored in a Google BigQuery database, so we'll need BigQuery credentials to access the data. From the [Google Cloud console](https://console.cloud.google.com/), enable the BigQuery API, then generate and download the corresponding service account credentials. Move them into the root directory of this repo as "credentials.json", and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable accordingly (see environment variable setup below).

### Google Cloud Storage

The network graph objects are so large that trying to construct them on a laptop is not feasible due to memory constraints. So we need to run various graph construction scripts on a larger remote server. Storage on Heroku servers is ephemeral, so we'll save the files to a Google Cloud Storage bucket instead. Create a new bucket or gain access to an existing bucket, and set the `GCS_BUCKET_NAME` environment variable accordingly (see environment variable setup below).

FYI: in the bucket, there will also exist some temporary tables used by BigQuery during batch job performances, so we're namespacing the storage of graph data under "storage/data", which is a mirror of the local "data" directory.

### SendGrid Emails

The app will run scripts that take a long time. To have those scripts send emails when they are done, first obtain a [SendGrid API Key](https://app.sendgrid.com/settings/api_keys), then set it as an environment variable (see environment variable setup below).

### Local Database

To download some of the data from BigQuery into a local database, first create a local PostgreSQL database called something like "impeachment_analysis", then set the `DATABASE_URL` environment variable accordingly (see environment variable setup below).

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

# SENDGRID_API_KEY="__________"
# MY_EMAIL_ADDRESS="hello@example.com"

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
```

Testing the Google Cloud Storage connection, saving some mock files in the specified bucket:

```sh
python -m app.gcs_service
```

Renaming files on Google Cloud Storage, if necessary:

```sh
EXISTING_PATTERN="storage/data/2020-" EXISTING_DIRPATH="storage/data" NEW_DIRPATH="storage/data/archived_graphs" python -m app.gcs_file_renaming

EXISTING_DIRPATH="storage/data/archived_graphs" NEW_DIRPATH="storage/data/archived" python -m app.gcs_file_renaming
```

## Testing

Run tests:

```sh
APP_ENV="test" pytest
```

## [Deploying](/DEPLOYING.md)

## [License](/LICENSE.md)
