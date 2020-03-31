
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
conda create -n tweets-env python=3.7 # (first time only)
conda activate tweets-env
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
USERS_LIMIT=5000
BATCH_SIZE=100
#MIN_USER_ID="________"
#MAX_USER_ID="_______"

# GOOGLE APIs
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
BIGQUERY_PROJECT_NAME="tweet-collector-py"
BIGQUERY_DATASET_NAME="impeachment_development"
```

### Google API Credentials

From the Google Cloud console, enable the BigQuery API, then generate and download the corresponding service account credentials (for example into the root directory of this repo as "credentials.json") and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable accordingly.

## Usage

Fetch data from Twitter:

```sh
python -m app.twitter_scraper
```

Fetch data from BigQuery:

```sh
python -m app.storage_service
```

If both of those commands work, you can collect the friend graphs, which will be stored in a new table on BigQuery:

```sh
python -m app.collect_friends
```

## [License](/LICENSE.md)
