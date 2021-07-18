
# User Timelines Collection

Adapted from: https://github.com/s2t2/tweet-analysis-2021/blob/main/app/jobs/timeline_collection.py

## Migrations

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.timeline_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.timeline_lookups` (
    user_id INT64,
    timeline_length INT64,
    error_type STRING,
    error_message STRING,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
);
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.timeline_tweets`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.timeline_tweets` (
    user_id INT64,
    status_id INT64,
    status_text STRING,
    created_at TIMESTAMP,

    geo STRING,
    is_quote BOOLEAN,
    truncated BOOLEAN,

    reply_status_id INT64,
    reply_user_id INT64,
    retweeted_status_id INT64,
    retweeted_user_id INT64,
    retweeted_user_screen_name STRING,

    urls ARRAY<STRING>,

    lookup_at TIMESTAMP
)
```

## Queries

Monitoring the results:

```sql
SELECT
  error_message
  ,count(distinct user_id) as user_count
  ,sum(timeline_length) as tweet_count
  ,avg(timeline_length) as tweet_avg
FROM `tweet-collector-py.impeachment_production.timeline_lookups`
GROUP BY 1
--ORDER BY  start_at desc
--LIMIT 10
```

```sql
-- see: https://developer.twitter.com/ja/docs/basics/response-codes
SELECT
    error_type
    ,error_code
    ,case when error_message like "%401%" THEN "Unauthorized"
        when error_message like "%500%" THEN "Internal Server Error"
        when error_message like "%503%" THEN "Service Unavailable"
        else error_message
    end error_message
   ,count(distinct user_id) as user_count
   ,sum(timeline_length) as tweet_count
FROM `tweet-collector-py.impeachment_production.timeline_lookups`
group by 1,2,3
order by user_count desc
```

## Usage

Continuous collection of tweet timelines, specifying the max number of users to fetch, and the max number of tweets per user (it also uses their last tweet id if we have it):

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.jobs.timeline_collection
```
