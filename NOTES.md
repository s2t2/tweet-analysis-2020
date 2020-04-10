# Notes

## Database Queries

### Tweets

Counting users and tweets:

```sql
SELECT
  count(DISTINCT user_id) as user_count -- 3,600,545
  ,count(DISTINCT status_id) as tweet_count -- 67,655,058
FROM impeachment_production.tweets
```

tweet_count	| user_count
---	        | ---
67,655,058	| 3,600,545

Counting users and tweets per month:

```sql
SELECT
  EXTRACT(YEAR from created_at) as year
  ,EXTRACT(MONTH from created_at) as month
  ,min(EXTRACT(DAY from created_at)) as first_day
  ,max(EXTRACT(DAY from created_at)) as last_day
  ,count(DISTINCT status_id) as tweet_count
  ,count(DISTINCT user_id) as user_count
FROM impeachment_production.tweets
GROUP BY 1,2
ORDER BY 1,2
```

year	| month	| first_day	| last_day  | tweet_count	| user_count
---	    | ---	| ---	    | ---       | ---	        | ---
2019	| 12	| 2	        | 31        | 18,239,072	| 1,860,878
2020	| 1	    | 1	        | 31        | 31,504,261	| 2,105,059
2020	| 2	    | 1	        | 29        | 14,207,862	| 1,416,178
2020	| 3	    | 1	        | 24        | 3,715,362	    | 789,737

Over 67.6M tweets from over 3.6M users were collected during the period from December 2, 2019 through March 24, 2020.

### Topics

Listing topics (25):

```sql
SELECT *
FROM impeachment_production.topics
```

topic	                | created_at
---	                    | ---
Trump to Pelosi	        | 2019-12-17 17:48:23 UTC
#ImpeachAndConvictTrump	| 2019-12-17 17:48:23 UTC
#IGHearing	            | 2019-12-17 17:48:23 UTC
impeach	                | 2019-12-17 17:48:23 UTC
#ImpeachAndConvict	    | 2019-12-17 17:48:23 UTC
#TrumpImpeachment	    | 2019-12-17 17:48:23 UTC
#IGReport	            | 2019-12-17 17:48:23 UTC
impeached	            | 2019-12-17 17:48:23 UTC
#SenateHearing	        | 2019-12-17 17:48:23 UTC
impeachment	            | 2019-12-17 17:48:23 UTC
#FactsMatter	        | 2019-12-17 17:48:23 UTC
#ImpeachmentRally	    | 2019-12-18 06:37:35 UTC
#ImpeachmentEve	        | 2019-12-18 06:18:08 UTC
#ImpeachAndRemove	    | 2019-12-18 06:35:29 UTC
#trumpletter	        | 2019-12-18 06:29:40 UTC
#NotAboveTheLaw	        | 2019-12-18 07:42:53 UTC
#25thAmendmentNow	    | 2019-12-18 07:42:16 UTC
#ShamTrial	            | 2020-01-22 03:59:06 UTC
#GOPCoverup	            | 2020-01-22 03:59:24 UTC
#MitchMcCoverup	        | 2020-02-06 01:37:48 UTC
#AquittedForever	    | 2020-02-06 01:37:05 UTC
#CoverUpGOP	            | 2020-02-06 01:36:36 UTC
#MoscowMitch	        | 2020-02-06 01:37:30 UTC
#CountryOverParty	    | 2020-02-06 01:37:13 UTC

## Partitioning Users

Will be running friend collection in a distributed way, so fetching buckets of users to assign to each server at one time or another.

```sql
SELECT
  partition_id
  ,count(DISTINCT user_id) as user_count
  ,min(user_id) as min_id
  ,max(user_id) as max_id
FROM (
  SELECT
    NTILE(10) OVER (ORDER BY CAST(user_id as int64)) as partition_id
    ,CAST(user_id as int64) as user_id
  FROM (SELECT DISTINCT user_id FROM impeachment_production.tweets)
) user_partitions
GROUP BY partition_id
```

partition_id    | user_count	| min_id	            | max_id
---	            | ---	        | ---	                | ---
1	            | 360055	    | 17	                | 49223966
2	            | 360055	    | 49224083	            | 218645473
3	            | 360055	    | 218645600	            | 446518003
4	            | 360055	    | 446520525	            | 1126843322
5	            | 360055	    | 1126843458	        | 2557922900
6	            | 360054	    | 2557923828	        | 4277913148
7	            | 360054	    | 4277927001	        | 833566039577239552
8	            | 360054	    | 833567097506533376	| 1012042187482202113
9	            | 360054	    | 1012042227844075522	| 1154556355883089920
10	            | 360054	    | 1154556513031266304	| 1242523027058769920

## Targets, Benchmarks, and Constraints

### Clock Time

With 3.6M users, processing 360K users per day would take ten days. Ten days would be ideal, but even up to a month would be fine.

Users per Day (Target) | Duration Days (Projected)
-- | --
360,000 | 10
324,000 | 11
288,000 | 13
252,000 | 14
216,000 | 17
180,000 | 20
144,000 | 25
115,200 | 31
108,000 | 33
86,400 | 42

### Twitter API

Currently Twitter API restricts to [15 requests per 15 minutes](https://developer.twitter.com/en/docs/basics/rate-limits), which is like 1 user per minute. So we need to use a custom scraper approach.

Using the custom scraper takes around 40 seconds for a user who has 2000 friends (our current max). So we need to leverage concurrent (i.e. a multi-threaded) processing approach.

### Servers and Costs

Target budget for this process is around $100, but can go up to around $200.

Heroku Server Tier | Memory | Max Threads | Cost per Month
-- | -- | -- | --
free | 512 MB | 256 | $0
hobby | 512 MB | 256 | $7
standard-1x | 512 MB | 256 | $25
standard-2x | 1 GB | 512 | $50
performance-m | 2.5 GB | 16,384 | $250
performance-l | 14 GB | 32,768 | $500

Running timed trials on different kinds of Heroku servers, with different concurrency configurations (i.e. max threads), to determine the optimal cost and time results. Example configuration:

```sh
USERS_LIMIT=5000 BATCH_SIZE=20 MAX_THREADS=50 python -m app.workers.batch_per_thread
```

Monitoring results for each trial via this query (adjusting the `start_at` and `end_at` as applicable):

```sql

SELECT
   min(start_at) as min_start
   ,max(end_at) as max_end
   ,count(user_id) as row_count
   ,count(distinct user_id) as user_count
   ,DATETIME_DIFF(max(CAST(end_at as DATETIME)), min(cast(start_at as DATETIME)), MINUTE) as runtime_mins
   ,round(avg(runtime_seconds),4) as avg_run_seconds
   ,round(avg(friend_count),2) as avg_friends
FROM (
  SELECT
    user_id
    ,screen_name
    ,friend_count
    ,start_at
    ,end_at
    ,DATETIME_DIFF(CAST(end_at as DATETIME), cast(start_at as DATETIME), SECOND) as runtime_seconds
  FROM impeachment_production.user_friends
  WHERE start_at > "2020-04-10 15:55:00"
  -- WHERE start_at BETWEEN "2020-04-08 00:50:00" AND "2020-04-08 04:25:00"
) subq


/*
select user_id,	screen_name,	friend_count,	start_at,	end_at
from impeachment_production.user_friends
where start_at > "2020-04-10 15:55:00"
order by end_at DESC
*/

/*
select count(user_id) as row_count, count(distinct user_id) as user_count
from impeachment_production.user_friends
where start_at > "2020-04-10 15:55:00"
*/

```

Not all timed trials have been successful. Some continue to run threads but stop storing results in the database. Increasing the thread count has diminishing returns, and when increased significantly, seems to cease storing results in the database. So we're going with multiple smaller servers.
