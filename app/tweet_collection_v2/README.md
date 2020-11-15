# Tweet Collection v2

## CSV File Storage

Make a directory in the "data/tweet_collection_v2" dir called something like "transition_2021", for your own event name. In it create a "topics.csv" file with contents like:

    topic
    #StopTheSteal
    #SharpieGate
    #RiggedElection
    #TrumpConceded

> FYI: the first row "topic" is a required column header. Twitter will match these topics case-insensitively and inclusively, so a topic of "rain" would include tweets about "#Rainbows".

> FYI if you pick too broad topics, the rate limiting might become a problem. prefer to collect a narrow set of topics on a single server with a single set of api keys.

Collecting tweets locally (where `EVENT_NAME` is the directory where the local "topics.csv" file is stored):

```sh
STORAGE_ENV="local" EVENT_NAME="transition_2021" python -m app.tweet_collection_v2.stream_listener
```

## BigQuery Storage (Development Database)

Create a development database on BigQuery called something like "transition_2021_development".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="transition_2021_development" EVENT_NAME="transition_2021" python -m app.tweet_collection_v2.bq_migrations
```

Collecting tweets to the development database:

```sh
BIGQUERY_DATASET_NAME="transition_2021_development" STORAGE_ENV="remote" python -m app.tweet_collection_v2.stream_listener
```

# Deploying

First create a new production database on BigQuery called something like "transition_2021_production".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="transition_2021_production" EVENT_NAME="transition_2021" python -m app.tweet_collection_v2.bq_migrations
```


Create and configure a new server:

```sh
heroku create -n transition-2021-collection
git remote add transition-collection https://git.heroku.com/transition-2021-collection.git

heroku buildpacks:set heroku/python -r transition-collection
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack -r transition-collection
heroku config:set GOOGLE_CREDENTIALS="$(< credentials.json)" -r transition-collection # references local creds
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json" -r transition-collection
```

Create bucket called "transition-2021".

Then set env vars on the server:

```sh
heroku config:set APP_ENV="production" -r transition-collection
heroku config:set SERVER_NAME="transition-2021" -r transition-collection # or whatever yours is called

heroku config:set STORAGE_ENV="remote" -r transition-collection
heroku config:set BIGQUERY_DATASET_NAME="transition_2021_production" -r transition-collection
heroku config:set BATCH_SIZE="125" -r transition-collection
heroku config:set GCS_BUCKET_NAME="transition-2021" -r transition-collection

heroku config:set TWITTER_CONSUMER_KEY="__________" -r transition-collection
heroku config:set TWITTER_CONSUMER_SECRET="__________" -r transition-collection
heroku config:set TWITTER_ACCESS_TOKEN="____________" -r transition-collection
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="_______________" -r transition-collection


```

Deploying:

```sh
git push transition-collection master
```

Finally, manually turn on the "tweet_collector" dyno (Hobby tier is fine) to collect tweets to the production database.

And view logs as desired:

```sh
heroku logs --tail
```
