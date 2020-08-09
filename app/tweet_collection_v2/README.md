# Tweet Collection v2

## CSV File Storage

Make a directory "data/tweet_collection_v2/election_2020". In it create a "topics.csv" file with contents like:

    topic
    Biden
    Trump
    #Election2020
    #2020Election
    #MAGA
    #KAG2020

Collecting tweets:

```sh
STORAGE_ENV="local" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.stream_listener
```

## BigQuery Storage (Development Database)

Create the dataset "election_2020_development" on BigQuery.

Migrate tables and seed topics:

```sh
BIGQUERY_DATASET_NAME="election_2020_development" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.bq_migrations
```

Collecting tweets:

```sh
BIGQUERY_DATASET_NAME="election_2020_development" STORAGE_ENV="remote" python -m app.tweet_collection_v2.stream_listener
```

# Deploying

First create a new dataset called "election_2020_production" on BigQuery.

Migrate the tables on production, adding topics from the local CSV file (you can also run this anytime you need to add topics on production, just reset the tweet collector afterwards):

```sh
BIGQUERY_DATASET_NAME="election_2020_production" EVENT_NAME="election_2020" python -
m app.tweet_collection_v2.bq_migrations
```

Then set env vars on the server:

```sh
heroku config:unset MAX_THREADS -r heroku
heroku config:unset USERS_LIMIT -r heroku

heroku config:set BATCH_SIZE="125" -r heroku

heroku config:set TWITTER_CONSUMER_KEY="__________" -r heroku
heroku config:set TWITTER_CONSUMER_SECRET="__________" -r heroku
heroku config:set TWITTER_ACCESS_TOKEN="____________" -r heroku
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="_______________" -r heroku

heroku config:set STORAGE_ENV="remote" -r heroku
heroku config:set BIGQUERY_DATASET_NAME="election_2020_production" -r heroku
```

Deploying:

```sh
git push heroku master
# git push heroku collection-2:master -f
```

Finally, manually turn on the "tweet_collector" dyno (Hobby tier is fine). And view logs as desired:

```sh
heroku logs --tail -r heroku
```
