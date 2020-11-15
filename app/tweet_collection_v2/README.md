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
    #DNCC
    #RNCC
    President T
    Kamala
    Pence
    WhiteHouse
    POTUS
    #BuildBackBetter
    TeamTrump
    TeamJoe
    88022
    30330
    #FillTheSeat
    #FillThatSeat
    #Debates2020
    #Vote2020
    #ElectionDay
    #ElectionDay2020
    #ElectionNight
    #ElectionNight2020
    #KAG
    #StopTheSteal
    #SharpieGate
    #RiggedElection


> FYI: the first row "topic" is a required column header. Twitter will match these topics case-insensitively and inclusively, so a topic of "rain" would include tweets about "#Rainbows".


Collecting tweets locally (where `EVENT_NAME` is the directory where the local "topics.csv" file is stored):

```sh
STORAGE_ENV="local" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.stream_listener
```

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

# Deploying

First create a new production database on BigQuery called something like "election_2020_production".

Migrate its tables and seed topics from the local CSV file:

```sh
BIGQUERY_DATASET_NAME="election_2020_production" EVENT_NAME="election_2020" python -m app.tweet_collection_v2.bq_migrations
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

Finally, manually turn on or restart the "tweet_collector" dyno (Hobby tier is fine) to collect tweets to the production database.

And view logs as desired:

```sh
heroku logs --tail
```
