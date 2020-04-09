# Reproducibility Notes

## Notebook Conversion

Uploaded / imported [this notebook](/start/follower_network_collector.ipynb) [into colab](https://colab.research.google.com/drive/1T0ED71rbhiNF8HG-769aBqA0zZAJodcd), then selected "File" > "Download .py" and stored the [resulting python script](/start/follower_network_collector.py) in the "start" dir.

## Database Resources

Working with BigQuery:

  + https://cloud.google.com/bigquery/docs/reference/standard-sql/operators
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules
  + https://cloud.google.com/dataprep/docs/html/DATEDIF-Function_57344707
  + https://towardsdatascience.com/google-bigquery-sql-dates-and-times-cheat-sheet-805b5502c7f0
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions

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





## Twitter Resources

Ad-hoc conversions between user ids and screen names:
  + https://tweeterid.com/

Working with the `twint` package:
  + https://github.com/twintproject/twint
  + https://pielco11.ovh/posts/twint-osint/#followersfollowing
  + https://github.com/twintproject/twint/pull/685
  + https://github.com/twintproject/twint/wiki/Storing-objects-in-RAM
  + https://github.com/twintproject/twint/issues/270
  + https://github.com/twintproject/twint/issues/704

> NOTE: deciding ultimately not to go with the twint package. was able to use a custom scraper which seems to be faster.


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

## Increasing Performance Capacity

With 3.6M users, with 10 servers over 10 days, we'd need to process an average of 360K users per server per day. This is a **goal of at least 25 users per minute**.

Currently Twitter API restricts to 15 requests per 15 minutes, which is like 1 user per minute. In the rate limit guide, it suggests there might be a way to make 180 requests per 15 minutes, which is like 12 users per minute. This would get us half-way to the goal. Would need to figure out how to get approved for the increased capacity. Update: this table shows the [break-down of limits for each kind of API call](https://developer.twitter.com/en/docs/basics/rate-limits), for each kind of API auth strategy.

Based on the performance logging so far, the Twint package takes 1-2 minutes to collect friends for each user.

Neither of these approaches is currently going to get us the desired performance at scale.

Resources and Research into multiple threads:

  + https://docs.python.org/3/library/threading.html
  + https://realpython.com/intro-to-python-threading/
  + https://pymotw.com/2/threading/

### Threading on Heroku

Heroku says it can support up to 256 threads on the free tier. So let's try to take advantage of that capability.

  + https://stackoverflow.com/questions/38632621/can-i-run-multiple-threads-in-a-single-heroku-python-dyno
  + https://devcenter.heroku.com/articles/limits#processes-threads
  + https://devcenter.heroku.com/articles/dynos#process-thread-limits

When running the multi-threaded approach on Heroku however, we are seeing "RuntimeError: can't start new thread" errors when the number of threads is set to anything more than 10.

```sh
USERS_LIMIT=40 MAX_THREADS=10 BATCH_SIZE=5 python -m app.friend_collector #> OK ON HEROKU
USERS_LIMIT=40 MAX_THREADS=15 BATCH_SIZE=5 python -m app.friend_collector #> FAIL ON HEROKU
```

Interestingly enough, the example executor script is able to run on Heroku and my local machine with 100 threads. But the friend collector won't run on either machine with that number of threads.

```sh
USERS_LIMIT=500 MAX_THREADS=100 BATCH_SIZE=50 python -m app.executor #> OK ON HEROKU AND LOCAL

USERS_LIMIT=500 MAX_THREADS=100 BATCH_SIZE=50 python -m app.friend_collector #> FAIL ON HEROKU
#> RuntimeError: can't start new thread

USERS_LIMIT=500 MAX_THREADS=100 BATCH_SIZE=50 python -m app.friend_collector #> FAIL ON LOCAL
#> AttributeError: '_UnixSelectorEventLoop' object has no attribute '_ssock'
```

Maybe we are hitting memory capacity on Heroku. Checking the performance metrics might help...

Memory load was high. Dyno load was high as well. Scaling up the dyno seems to alleviate the situation. Maybe it was a memory capacity thing.



Monitoring results...

```sql
/*
select
  count(distinct screen_name) as user_count
FROM impeachment_production.user_friends
*/

/*
select
  -- count(distinct screen_name) as user_count
  screen_name
  ,end_at
FROM impeachment_production.user_friends
WHERE end_at BETWEEN "2020-04-03 02:30:00" AND "2020-04-03 03:50:00"
order by end_at
*/


SELECT
   count(distinct user_id) as user_count
   ,DATETIME_DIFF(max(CAST(end_at as DATETIME)), min(cast(start_at as DATETIME)), MINUTE) as runtime_mins
   -- ,count(distinct screen_name) as name_count
   --,sum(if(friend_count > 0, 1, 0)) as users_with_friends
   -- ,count(distinct if(friend_count > 0, user_id, NULL)) as users_with_friends
   -- ,min(runtime_seconds) as shortest_run_seconds
   -- ,max(runtime_seconds) as longest_run_seconds
   ,round(avg(runtime_seconds),4) as avg_run_seconds
   --,min(friend_count) as min_friends
   --,max(friend_count) as max_friends
   ,round(avg(friend_count),2) as avg_friends
   -- ,round(avg(friend_count/runtime_seconds),2) as avg_friends_per_second
FROM (
  SELECT
    user_id
    ,screen_name
    ,friend_count
    ,start_at
    ,end_at
    ,DATETIME_DIFF(CAST(end_at as DATETIME), cast(start_at as DATETIME), SECOND) as runtime_seconds
  FROM impeachment_production.user_friends
  WHERE start_at BETWEEN "2020-04-08 00:50:00" AND "2020-04-08 04:25:00"
) subq
```

Current best working results on Heroku "performance-m" ($250/mo) server are something like:

```sh
USERS_LIMIT=1000 BATCH_SIZE=20	MAX_THREADS=200
```

### Avoiding Race Conditions

So, the threads were all doing their jobs, but the results weren't reliably getting stored in the database. Perhaps due to race-conditions around clearing of the batch of users that are to be stored. Perhaps the batches were being cleared so the condition was never getting reached. Looking into locking and semaphores, which are supposed to be desired to help this situation.

Resources:

  + https://docs.python.org/3.7/library/threading.html#threading.Lock
  + https://docs.python.org/3.7/library/threading.html#threading.Semaphore
  + https://docs.python.org/3.7/library/threading.html#threading.BoundedSemaphore
  + https://stackoverflow.com/questions/48971121/what-is-the-difference-between-semaphore-and-boundedsemaphore
  + https://www.pythonstudio.us/reference-2/semaphore-and-bounded-semaphore.html

Seems to be helping the situation.
