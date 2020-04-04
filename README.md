
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

Fetch example data from Twitter:

```sh
SCREEN_NAME="elonmusk" python -m app.twitter_scraper
SCREEN_NAME="barackobama" python -m app.twitter_scraper
```

Fetch users from BigQuery:

```sh
python -m app.storage_service
```

If both of those commands work, you can collect the friend graphs, which will be stored in a new table on BigQuery:

```sh
python -m app.multithreaded.friend_collector
# ... or specify confg vars:
USERS_LIMIT=40 MAX_THREADS=10 BATCH_SIZE=5 python -m app.friend_collector
```

## [Deploying](/DEPLOYING.md)

## [License](/LICENSE.md)
