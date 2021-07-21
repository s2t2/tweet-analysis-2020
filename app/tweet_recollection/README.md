## Tweet Collection Again

Requirements (two birds one stone):

  1. We have retweets of the original tweet, but in some cases not the original tweet itself, so let's lookup the original tweets (retweets, and replies while we're at it).
  2. Some of the texts are truncated. It would be nice to have non-truncated / full texts (really this time).
  3. We need the full, non-truncated url(s) shared in the tweet text (so we can do news credibility analysis on the domains).

Limitations:
  + Some user accounts have been deactivated.
  + Some of the original tweets have since been deleted.


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


Now making tables to store the new lookups and the full tweet info:

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.all_status_id_lookups`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.all_status_id_lookups` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.all_status_id_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.all_status_id_lookups` (
    status_id INT64,
    lookup_at TIMESTAMP,
    error_type STRING,
    error_message STRING,
)

--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_statuses`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_statuses` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.recollected_statuses`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.recollected_statuses` (
    status_id INT64,
    full_text STRING,
    created_at TIMESTAMP,

    user_id INT64,
    user_screen_name STRING,

    entity_urls ARRAY<STRING>
)
```

Query to see which statuses have not yet been looked-up:

```sql
SELECT DISTINCT ids.status_id
FROM `tweet-collector-py.impeachment_production.all_status_ids` ids
LEFT JOIN `tweet-collector-py.impeachment_production.all_status_id_lookups` lookups
  ON lookups.status_id = ids.status_id
WHERE lookups.status_id IS NULL
--LIMIT 10
```

## Usage

Run the job:

```sh
BIGQUERY_DATASET_NAME="impeachment_development" STATUS_LIMIT=10 BATCH_SIZE=10  python -m app.tweet_recollection.second_passer
```
