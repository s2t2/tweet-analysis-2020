# Tweet Collection v2

## CSV File Storage

Make a directory in the "data/tweet_collection_v2" dir called something like "election_2020", for your own event name. In it create a "topics.csv" file with contents like:

    topic
    Biden
    Trump
    #Election2020
    #2020Election
    #MAGA
    #KAG2020
    #creepyjoe
    #sleepyjoe
    #voteblue

> FYI: the first row "topic" is a required column header. Twitter will match these topics case-insensitively and inclusively, so a topic of "rain" would include tweets about "#Rainbows".

> GUIDANCE: a narrow set of specific hashtags (i.e. "TrumpImpeachment") may be less likely to encounter crushing rate limits than a broader set of keywords (i.e. "impeach")


Collecting tweets locally (where `EVENT_NAME` is the directory where the local "topics.csv" file is stored):

```sh
STORAGE_ENV="local" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.stream_listener
```

> NOTE: run this for a while and make sure you aren't getting rate limited too bad, otherwise try removing some topics / splitting topics across more collection servers. it is harder to remove a topic once it has hit the remote databases...

## BigQuery Storage (Development Database)

Create a development database on BigQuery called something like "election_2020_development".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="election_2020_development" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.bq_migrations
```

Collecting tweets to the development database:

```sh
BIGQUERY_DATASET_NAME="election_2020_development" STORAGE_ENV="remote" python -m app.tweet_collection_v2.stream_listener
```

## BigQuery Storage (Production Database)

First create a new production database on BigQuery called something like "election_2020_production".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="election_2020_production" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.bq_migrations
```



# Deploying

## Server Setup

Create a new app server (first time only):

```sh
heroku create impeachment-tweet-analysis # (use your own app name here)
```

## Server Config

Provision and configure the Google Application Credentials Buildpack to generate a credentials file on the server:

```sh
heroku buildpacks:set heroku/python
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack
heroku config:set GOOGLE_CREDENTIALS="$(< credentials.json)" # references local creds
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json"
```

Configure the rest of the environment variables (see [Partitioning Users](/NOTES.md#partitioning-users)):

```sh
heroku config:set APP_ENV="production"
heroku config:set SERVER_NAME="impeachment-tweet-analysis-10" # or whatever yours is called

heroku config:set BIGQUERY_DATASET_NAME="impeachment_production"
heroku config:set GCS_BUCKET_NAME="impeachment-analysis-2020" -r heroku-4

heroku config:set SENDGRID_API_KEY="_____________"
heroku config:set MY_EMAIL_ADDRESS="me@example.com"

# EXAMPLE JOB-SPECIFIC CONFIG VARS...
#heroku config:set MIN_USER_ID="17"
#heroku config:set MAX_USER_ID="49223966"
#heroku config:set USERS_LIMIT="10000"
#heroku config:set BATCH_SIZE="20"
#heroku config:set MAX_THREADS="20"
```




## Deployment

Deploy:

```sh
# from master branch
git checkout master
git push heroku master

# or from another branch
git checkout mybranch
git push heroku mybranch:master
```






Then set env vars on the server:

```sh
heroku config:set TWITTER_CONSUMER_KEY="__________"
heroku config:set TWITTER_CONSUMER_SECRET="__________"
heroku config:set TWITTER_ACCESS_TOKEN="____________"
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="_______________"

heroku config:set STORAGE_ENV="remote"
heroku config:set BIGQUERY_DATASET_NAME="election_2020_production"

heroku config:set BATCH_SIZE="125"
```

Deploying:

```sh
git push heroku master
# git push heroku collection-2:master -f
```

Finally, manually turn on the "tweet_collector" dyno (Hobby tier is fine) to collect tweets to the production database.

And view logs as desired:

```sh
heroku logs --tail
```
