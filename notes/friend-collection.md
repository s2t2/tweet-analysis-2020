



# Friend Collection Notes

## Partitioning Users

Will be running friend collection in a distributed way (across multiple servers, with each server processing a batch of users), so assigning users to buckets:

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

## Clock Time Constraints

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

## Twitter API Constraints

Currently Twitter API restricts to [15 requests per 15 minutes](https://developer.twitter.com/en/docs/basics/rate-limits), which is like 1 user per minute. So we need to use a custom scraper approach.

Using the custom scraper takes around 40 seconds for a user who has 2000 friends (our current max). So we need to leverage concurrent (i.e. a multi-threaded) processing approach.

## Server Cost Constraints

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
USERS_LIMIT=5000 BATCH_SIZE=20 MAX_THREADS=50 python -m app.app.friend_graphs.collect_in_batches
```

## Friend Collection

Fetching user friends (people they follow), and storing them in the "user_friends" table on BigQuery:

```sh
python -m app.app.friend_graphs.collect_in_batches
# USERS_LIMIT=100 MAX_THREADS=3 BATCH_SIZE=10 python -m app.app.friend_graphs.collect_in_batches
```

## Monitoring Results


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

Selected Results (where "Thread Coordination" refers to `friend_collector.py`, and "Batch per Thread" refers to `friend_batch_collector.py`):


Dynos | Type | USERS LIMIT | BATCH SIZE | MAX THREADS | Worker | Status | Start | End | Users Collected | Runtime Mins | Seconds per User | Friends Per User | Users Per Min | Users Per Hr | Users Per Day
-- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --
1 | standard-2x | 100 | 20 | 3 | Thread Coordination | FAILED TO SAVE AFTER A WHILE | "2020-04-08 00:50:00" | "2020-04-08 04:25:00" | 1,688 | 214 | 17.2 | 972.5 | 7.9 | 473 | 11,359
1 | standard-2x | 500 | 100 | 15 | Thread Coordination | FAILED TO SAVE AFTER A WHILE | "2020-04-08 04:55:00" | "2020-04-08 13:35:00" | 5,586 | 519 | 56.4 | 925.4 | 10.8 | 646 | 15,499
1 | standard-2x | 5,000 | 100 | 30 | Thread Coordination | FAILED TO SAVE AFTER A WHILE | "2020-04-08 19:40:00" |   | 1,000 |   |   |   | #DIV/0! | #DIV/0! | #DIV/0!
1 | standard-2x | 5,000 | 20 | 50 | Batch per Thread | SUCCESSFUL | "2020-04-09 04:45:00" | "2020-04-09 15:21:09" | 13,447 | 631 | 129.1 | 470.8 | 21.3 | 1,279 | 30,687
1 | standard-2x | 10,000 | 20 | 100 | Batch per Thread | SUCCESSFUL | "2020-04-09 15:30:00" | "2020-04-09 21:18:00" | 8,016 | 347 | 221.8 | 464.0 | 23.1 | 1,386 | 33,265
1 | standard-2x | 5,000 | 20 | 250 | Batch per Thread | FAILED TO SAVE AFTER A WHILE | "2020-04-09 21:25:00" | "2020-04-10 00:30:00" | 12,880 | 512.0 | 286.9 | 467.5 | 25.2 | 1,509 | 36,225
1 | performance-m | 50,000 | 20 | 2500 | Batch per Thread | FAILED TO SAVE BARELY ANYTHING | "2020-04-10 01:10:00" | "2020-04-10 04:25:00" | 40 | 191.0 | 442.4 | 214.0 | 0.2 | 13 | 302
1 | performance-m | 5,000 | 20 | 250 | Batch per Thread | SUCCESSFUL | "2020-04-10 04:35:00" | "2020-04-10 13:15:00" | 18,604 | 722.0 | 331.7 | 466.0 | 25.8 | 1,546 | 37,105
1 | standard-1x | 5,000 | 20 | 50 | Batch per Thread | IN PROGRESS | "2020-04-10 15:55:00" |   | 2,107 | 93.0 | 104.2 | 425.0 | 22.7 | 1,359 | 32,625


Not all timed trials have been successful. Some continue to run threads but stop storing results in the database. Increasing the thread count has diminishing returns, and when increased significantly, seems to cease storing results in the database. So we're going with multiple smaller servers.












## Friend Collection Results

Verifying users have been bucketed properly:

```sql
SELECT assigned_server, count(distinct user_id) as user_count
FROM (
  SELECT
    user_id
    ,CASE
        WHEN CAST(user_id as int64) BETWEEN 17                  and 49223966 THEN "server-1"
        WHEN CAST(user_id as int64) BETWEEN 49224083            and 218645473 THEN "server-2"
        WHEN CAST(user_id as int64) BETWEEN 218645600           and 446518003 THEN "server-3"
        WHEN CAST(user_id as int64) BETWEEN 446520525           and 1126843322 THEN "server-4"
        WHEN CAST(user_id as int64) BETWEEN 1126843458          and 2557922900 THEN "server-5"
        WHEN CAST(user_id as int64) BETWEEN 2557923828          and 4277913148 THEN "server-6"
        WHEN CAST(user_id as int64) BETWEEN 4277927001          and 833566039577239552 THEN "server-7"
        WHEN CAST(user_id as int64) BETWEEN 833567097506533376  and 1012042187482202113 THEN "server-8"
        WHEN CAST(user_id as int64) BETWEEN 1012042227844075522 and 1154556355883089920 THEN "server-9"
        WHEN CAST(user_id as int64) BETWEEN 1154556513031266304 and 1242523027058769920 THEN "server-10"
     END as assigned_server
  FROM impeachment_production.users
)
GROUP BY assigned_server
ORDER BY assigned_server
```

Monitoring results as they come in:

```sql

SELECT
  assigned_server
  ,count(distinct user_id) as users_processed
  ,round(avg(friend_count),2) as avg_friends
  ,round(avg(runtime_seconds),4) as avg_run_seconds
  -- ,max(end_at) as latest_at
  -- ,360054 - count(distinct user_id) as users_remaining
FROM (
  SELECT
    user_id, friend_count, start_at, end_at
    ,DATETIME_DIFF(CAST(end_at as DATETIME), cast(start_at as DATETIME), SECOND) as runtime_seconds
    ,CASE
        WHEN user_id BETWEEN 17                  and 49223966            THEN "server-01"
        WHEN user_id BETWEEN 49224083            and 218645473           THEN "server-02"
        WHEN user_id BETWEEN 218645600           and 446518003           THEN "server-03"
        WHEN user_id BETWEEN 446520525           and 1126843322          THEN "server-04"
        WHEN user_id BETWEEN 1126843458          and 2557922900          THEN "server-05"
        WHEN user_id BETWEEN 2557923828          and 4277913148          THEN "server-06"
        WHEN user_id BETWEEN 4277927001          and 833566039577239552  THEN "server-07"
        WHEN user_id BETWEEN 833567097506533376  and 1012042187482202113 THEN "server-08"
        WHEN user_id BETWEEN 1012042227844075522 and 1154556355883089920 THEN "server-09"
        WHEN user_id BETWEEN 1154556513031266304 and 1242523027058769920 THEN "server-10"
     END as assigned_server
  FROM (
    SELECT CAST(user_id as int64) as user_id, friend_count, start_at, end_at
    FROM impeachment_production.user_friends
  ) zz
) yy
GROUP BY assigned_server
ORDER BY assigned_server
```

Final results:

assigned_server | users_processed | avg_friends | avg_run_seconds
-- | -- | -- | --
server-01 | 360,055 | 820 | 131
server-02 | 360,055 | 723 | 107
server-03 | 360,055 | 666 | 99
server-04 | 360,055 | 610 | 95
server-05 | 360,055 | 567 | 91
server-06 | 360,054 | 522 | 55
server-07 | 360,054 | 508 | 56
server-08 | 360,054 | 460 | 62
server-09 | 360,054 | 353 | 51
server-10 | 360,054 | 217 | 25


Interesting to see that newer users (the ones with greater / later ids) have less friends on average, and therefore took less time to parse. Again note we have capped max friends at 2000, which skews the avg friend count.
