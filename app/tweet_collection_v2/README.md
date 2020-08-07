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

## BigQuery Storage

Create the dataset "election_2020_development" on BigQuery.

Migrate tables:

```sh

```

Collecting tweets:

```sh
STORAGE_ENV="remote" python -m app.tweet_collection_v2.stream_listener
```
