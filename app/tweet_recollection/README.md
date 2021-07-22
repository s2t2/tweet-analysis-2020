## Tweet Re-Collection

Requirements (two birds one stone):

  1. We have retweets of the original tweet, but in some cases not the original tweet itself, so let's lookup the original tweets (retweets, and replies while we're at it).
  2. Some of the texts are truncated. It would be nice to have non-truncated / full texts (really this time).
  3. We need the full, non-truncated url(s) shared in the tweet text (so we can do news credibility analysis on the domains).

Limitations:
  + Some user accounts have been deactivated.
  + Some of the original tweets have since been deleted.

Strategy:
  + We're going to do a second pass over tall the tweet ids we have in the dataset, including retweet targets, and lookup their full text and urls.

## Queries and Migrations

```sql
SELECT count(distinct t.status_id)
FROM `tweet-collector-py.impeachment_production.tweets` t -- 67,666,557
WHERE t.retweet_status_id is null -- 11,759,296
```


```sql
SELECT
    cast(status_id as int64) as status_id
    ,cast(user_id as int64) as user_id
    ,status_text
    ,created_at
    ,cast(reply_status_id as int64) as reply_status_id
    ,cast(retweet_status_id as int64) as retweet_status_id
FROM `tweet-collector-py.impeachment_production.tweets` t
--WHERE reply_status_id is not null
-- WHERE retweet_status_id is not null
LIMIT 10
```

Let's union these with all the reply and retweet sources! And look them all up.

But first let's finally make a table with integer ids, for faster querying.

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.tweets_v2`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.tweets_v2` as (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.tweets_v2`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.tweets_v2` as (
    SELECT
        cast(status_id as int64) as status_id
        ,cast(user_id as int64) as user_id
        ,status_text
        ,created_at
        ,cast(reply_status_id as int64) as reply_status_id
        ,cast(retweet_status_id as int64) as retweet_status_id
    FROM `tweet-collector-py.impeachment_production.tweets` t
    --LIMIT 100000
)
```

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.all_status_ids`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.all_status_ids` as (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.all_status_ids`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.all_status_ids` as (
  SELECT DISTINCT status_id
  FROM (
    (
      SELECT DISTINCT status_id --, "status" as id_source
      FROM `tweet-collector-py.impeachment_production.tweets_v2` t
      WHERE reply_status_id IS NULL AND reply_status_id IS NULL
      --LIMIT 10
    )
    UNION ALL
    (
      SELECT DISTINCT reply_status_id as status_id --, "reply" as id_source
      FROM `tweet-collector-py.impeachment_production.tweets_v2` t
      WHERE reply_status_id IS NOT NULL
      --LIMIT 10
    )
    UNION ALL
    (
      SELECT DISTINCT retweet_status_id as status_id --, "retweet" as id_source
      FROM `tweet-collector-py.impeachment_production.tweets_v2` t
      WHERE retweet_status_id IS NOT NULL
      --LIMIT 10
    )
  )

)
```


Now making tables to store the new status and url lookups:

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_statuses`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_statuses` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.recollected_statuses`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.recollected_statuses` (
    status_id INT64,
    user_id INT64,
    full_text STRING,
    created_at TIMESTAMP,
    lookup_at TIMESTAMP
);

--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_status_urls`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_status_urls` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.recollected_status_urls`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.recollected_status_urls` (
    status_id INT64,
    expanded_url STRING,
    --unwound_url STRING,
    --unwound_title STRING,
    --unwound_description STRING,
);
```


Monitoring results:

```sql
SELECT
   count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
FROM `tweet-collector-py.impeachment_production.recollected_statuses`
```

```sql
SELECT
   count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
FROM `tweet-collector-py.impeachment_production.recollected_statuses`
```


## Usage

Run the job:

```sh
BIGQUERY_DATASET_NAME="impeachment_development" STATUS_LIMIT=250 BATCH_SIZE=100 python -m app.tweet_recollection.collector
```

## Deploying

Run this on server 6.

Configuring:

```sh
heroku config:set TWITTER_API_KEY="_________" -r heroku-6
heroku config:set TWITTER_API_KEY_SECRET="_______" -r heroku-6
heroku config:set TWITTER_ACCESS_TOKEN="________" -r heroku-6
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="____________" -r heroku-6
heroku config:set TWITTER_ENVIRONMENT_NAME="______" -r heroku-6
```

Deploying:

```sh
git push heroku-6 recollection:main -f
```

Turn on the "tweet_recollector" dyno.

Monitoring:

```sh
heroku logs --tail -r heroku-6
```
