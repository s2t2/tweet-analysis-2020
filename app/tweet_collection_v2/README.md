# Tweet Collection v2

## CSV File Storage

Make a directory in the "data/tweet_collection_v2" dir called something like "disinfo_2021", for your own event name. In it create a "topics.csv" file with contents like:

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


Collecting tweets locally (where `EVENT_NAME` is the directory where the local "topics.csv" file is stored):

```sh
STORAGE_ENV="local" EVENT_NAME="disinfo_2021" python -m app.tweet_collection_v2.stream_listener
```

## BigQuery Storage (Development Database)

Create a development database on BigQuery called something like "disinfo_2021_development".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="disinfo_2021_development" EVENT_NAME="disinfo_2021" python -m app.tweet_collection_v2.bq_migrations
```

Collecting tweets to the development database:

```sh
BIGQUERY_DATASET_NAME="disinfo_2021_development" STORAGE_ENV="remote" python -m app.tweet_collection_v2.stream_listener
```

# Deploying

First create a new production database on BigQuery called something like "disinfo_2021_production".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="disinfo_2021_production" EVENT_NAME="disinfo_2021" python -m app.tweet_collection_v2.bq_migrations
```



```sh
heroku create -n disinfo-2021-collection
git remote add disinfo-collection https://git.heroku.com/disinfo-2021-collection.git


heroku buildpacks:set heroku/python -r disinfo-collection
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack -r disinfo-collection
heroku config:set GOOGLE_CREDENTIALS="$(< credentials.json)" -r disinfo-collection # references local creds
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json" -r disinfo-collection
```

Create bucket called "disinfo-2021".

Then set env vars on the server:

```sh
heroku config:set APP_ENV="production" -r disinfo-collection
heroku config:set SERVER_NAME="disinfo-collection-1" -r disinfo-collection # or whatever yours is called

heroku config:set STORAGE_ENV="remote" -r disinfo-collection
heroku config:set BIGQUERY_DATASET_NAME="disinfo_2021_production" -r disinfo-collection
heroku config:set BATCH_SIZE="125" -r disinfo-collection
heroku config:set GCS_BUCKET_NAME="disinfo-2021" -r disinfo-collection

heroku config:set TWITTER_CONSUMER_KEY="__________" -r disinfo-collection
heroku config:set TWITTER_CONSUMER_SECRET="__________" -r disinfo-collection
heroku config:set TWITTER_ACCESS_TOKEN="____________" -r disinfo-collection
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="_______________" -r disinfo-collection


```

Deploying:

```sh
git push disinfo-collection master
```

Finally, manually turn on the "tweet_collector" dyno (Hobby tier is fine) to collect tweets to the production database.

And view logs as desired:

```sh
heroku logs --tail
```
