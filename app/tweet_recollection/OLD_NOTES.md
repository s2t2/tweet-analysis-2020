
> NOTE: As we were wanting to do some analysis based on tweet URLs and noticing our truncated tweets don't have full URLs, we were thinking about returning to scrape timlines of users in our dataset (considerations discussed in this doc). But instead we are going with the timeline recollection approach (see README file in this directory).


# Queries

The goal is to select users for timeline scraping.


```sql
select count(distinct user_id) as user_count
--from `tweet-collector-py.disinfo_2021_production.timeline_tweets` -- 259,034
-- from `tweet-collector-py.disinfo_2021_production.tweets` -- 479,998
-- from `tweet-collector-py.election_2020_production.tweets` -- 2,806,531
-- from `tweet-collector-py.impeachment_2021_production.tweets` -- 1,578,367

```


```sql
```

The joins are taking too long. let's fix this casting up-front:

```sql
drop table if exists `tweet-collector-py.impeachment_production.tweets_slim`;
create table if not exists `tweet-collector-py.impeachment_production.tweets_slim` as (
    SELECT cast(user_id as int64) as user_id, cast(status_id as int64) as status_id
    FROM `tweet-collector-py.impeachment_production.tweets`
)
```

```sql
drop table if exists `tweet-collector-py.disinfo_2021_production.tweets_slim`;
create table if not exists `tweet-collector-py.disinfo_2021_production.tweets_slim` as (
    SELECT cast(user_id as int64) as user_id, cast(status_id as int64) as status_id
    FROM `tweet-collector-py.disinfo_2021_production.tweets`
)
```

```sql
#StandardSQL

WITH all_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.impeachment_production.tweets_slim`
) -- 3,600,545

,collected_disinfo_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
) -- 259,034

SELECT
    count(distinct u.user_id) as user_count
    ,count(distinct case when qu.user_id is not null then u.user_id end) as q_user_count -- 138,072
    ,count(distinct case when qu.user_id is null then u.user_id end) as nonq_user_count -- 3,462,473
FROM all_users u
left join collected_disinfo_users qu ON qu.user_id = u.user_id

```

```sql
#StandardSQL

WITH all_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.impeachment_production.tweets_slim`
) -- 3,600,545

,disinfo_users as (
    SELECT DISTINCT user_id
    FROM `tweet-collector-py.disinfo_2021_production.tweets_slim`
) -- 479,998

,collected_disinfo_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
) -- 259,034

SELECT
    count(distinct au.user_id) as user_count
FROM all_users au
LEFT JOIN disinfo_users qu ON qu.user_id = au.user_id
LEFT JOIN collected_disinfo_users cqu ON cqu.user_id = au.user_id
WHERE qu.user_id is null AND cqu.user_id is null -- 3,359,798
```

There are 3.3M eligible users. Let's sample them by their characteristics. Is it possible to [stratify in BigQuery](https://stackoverflow.com/questions/52901451/stratified-random-sampling-with-bigquery)?

```sql
-- we want to stratify on is_bot, is_q, and opinion_community
SELECT user_id, created_on, is_bot, is_q, opinion_community
  --, status_count, friend_count, follower_count
FROM `tweet-collector-py.impeachment_production.user_details_v6_slim`
LIMIT 100
```


```sql
--SELECT user_id ,is_q ,is_bot ,opinion_community
SELECT count(distinct user_id) as user_count
FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M

--WHERE is_q = True -- 25,360
-- WHERE is_bot = True -- 24,150
-- WHERE opinion_community = 1 -- 1,316,569
-- WHERE opinion_community = 0 -- 2,283,976


-- LETS TAKE ALL BOTS, ALL Q, AND 25K random nonbot nonq lefties, AND 25K nonbot nonq righties
```

```sql
--SELECT user_id ,is_q ,is_bot ,opinion_community
--FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M

--WHERE is_q = True -- 25,360
-- WHERE is_bot = True -- 24,150
-- WHERE opinion_community = 1 -- 1,316,569
-- WHERE opinion_community = 0 -- 2,283,976


-- LETS TAKE ALL BOTS, ALL Q, AND 25K random nonbot nonq lefties, AND 25K nonbot nonq righties

--SELECT user_id ,is_q ,is_bot ,opinion_community
--FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
--WHERE is_q=True or is_bot=True
--LIMIT 10

--SELECT user_id ,is_q ,is_bot ,opinion_community
--FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
--WHERE is_q=False and is_bot=False and opinion_community=0
--ORDER BY rand()
--LIMIT 10

SELECT user_id ,is_q ,is_bot ,opinion_community
FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
WHERE is_q=False and is_bot=False and opinion_community=1
ORDER BY rand()
LIMIT 10
```


```sql
--SELECT user_id ,is_q ,is_bot ,opinion_community
--FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M

--WHERE is_q = True -- 25,360
-- WHERE is_bot = True -- 24,150
-- WHERE opinion_community = 1 -- 1,316,569
-- WHERE opinion_community = 0 -- 2,283,976


-- LETS TAKE ALL BOTS, ALL Q, AND 25K random nonbot nonq lefties, AND 25K nonbot nonq righties

(
  SELECT user_id ,is_q ,is_bot ,opinion_community
  FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
  WHERE is_q=True or is_bot=True
  -- TODO: where not already looked-up
  LIMIT 10
)
UNION ALL
(
  SELECT user_id ,is_q ,is_bot ,opinion_community
  FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
  WHERE is_q=False and is_bot=False and opinion_community=0
  -- TODO: where not already looked-up
  ORDER BY rand()
  LIMIT 10 -- LIMIT
)
UNION ALL
(
  SELECT user_id ,is_q ,is_bot ,opinion_community
  FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3.6M
  WHERE is_q=False and is_bot=False and opinion_community=1
  -- TODO: where not already looked-up
  ORDER BY rand()
  LIMIT 10 -- LIMIT
)
```



```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.timeline_lookups`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.timeline_lookups` (
--    user_id INT64,
--    timeline_length INT64,
--    error_type STRING,
--    error_message STRING,
--    start_at TIMESTAMP,
--    end_at TIMESTAMP,
--);
```

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.timeline_tweets`;
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.timeline_tweets` (
--    user_id INT64,
--    status_id INT64,
--    status_text STRING,
--    created_at TIMESTAMP,
--
--    geo STRING,
--    is_quote BOOLEAN,
--    truncated BOOLEAN,
--
--    reply_status_id INT64,
--    reply_user_id INT64,
--    retweeted_status_id INT64,
--    retweeted_user_id INT64,
--    retweeted_user_screen_name STRING,
--
--    urls ARRAY<STRING>,
--
--    lookup_at TIMESTAMP
--)
```
