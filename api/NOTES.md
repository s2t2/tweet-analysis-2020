# Notes - V0

## Queries

### User Tweets

How many tweets should we expect back max for any given user?

```sql
SELECT
  upper(t.user_screen_name)
  ,count(distinct t.status_id) as status_count
FROM impeachment_production.tweets t
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1000
-- 16K, 16K, 11K, 9K, tail out in the lower thousands
```

How many tweets on average?

```sql
SELECT max(status_count), avg(status_count)
FROM (
  SELECT
    upper(t.user_screen_name)
    ,count(distinct t.status_id) as status_count
  FROM impeachment_production.tweets t
  GROUP BY 1
  -- ORDER BY 2 DESC
)
-- 16 tweets on average. will be ok.
```

### Users Most Retweeted

Community-specific retweet tables:

```sql
DROP TABLE IF EXISTS impeachment_production.community_0_retweets;
CREATE TABLE impeachment_production.community_0_retweets AS (
  SELECT
      bu.community_id
      ,bu.user_id
      ,rt.user_screen_name
      ,rt.user_created_at
      ,rt.retweeted_user_id
      ,rt.retweeted_user_screen_name
      ,rt.status_id
      ,rt.status_text
      ,rt.created_at
  FROM impeachment_production.2_bot_communities bu
  JOIN impeachment_production.retweets_v2 rt on bu.user_id = cast(rt.user_id as int64)
  WHERE bu.community_id = 0
);

DROP TABLE IF EXISTS impeachment_production.community_1_retweets;
CREATE TABLE impeachment_production.community_1_retweets AS (
  SELECT
      bu.community_id
      ,bu.user_id
      ,rt.user_screen_name
      ,rt.user_created_at
      ,rt.retweeted_user_id
      ,rt.retweeted_user_screen_name
      ,rt.status_id
      ,rt.status_text
      ,rt.created_at
  FROM impeachment_production.2_bot_communities bu
  JOIN impeachment_production.retweets_v2 rt on bu.user_id = cast(rt.user_id as int64)
  WHERE bu.community_id = 1
);

```

Users most retweeted:

```sql
DROP TABLE IF EXISTS impeachment_production.community_0_users_most_retweeted;
CREATE TABLE impeachment_production.community_0_users_most_retweeted AS (
  SELECT
    community_id
    ,retweeted_user_screen_name
    ,count(distinct user_id) as retweeter_count
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.community_0_retweets
  GROUP BY 1,2
  ORDER BY 3 DESC
  LIMIT 1000
);

DROP TABLE IF EXISTS impeachment_production.community_1_users_most_retweeted;
CREATE TABLE impeachment_production.community_1_users_most_retweeted AS (
  SELECT
    community_id
    ,retweeted_user_screen_name
    ,count(distinct user_id) as retweeter_count
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.community_1_retweets
  GROUP BY 1,2
  ORDER BY 3 DESC
  LIMIT 1000
);
```

Statuses most retweeted:

```sql
DROP TABLE IF EXISTS impeachment_production.community_0_statuses_most_retweeted;
CREATE TABLE impeachment_production.community_0_statuses_most_retweeted AS (
  SELECT
    community_id
    ,retweeted_user_screen_name
    ,status_text
    ,count(distinct user_id) as retweeter_count
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.community_0_retweets
  GROUP BY 1,2,3
  ORDER BY retweet_count DESC
  LIMIT 1000
);

DROP TABLE IF EXISTS impeachment_production.community_1_statuses_most_retweeted;
CREATE TABLE impeachment_production.community_1_statuses_most_retweeted AS (
  SELECT
    community_id
    ,retweeted_user_screen_name
    ,status_text
    ,count(distinct user_id) as retweeter_count
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.community_1_retweets
  GROUP BY 1,2,3
  ORDER BY retweet_count DESC
  LIMIT 1000
);
```
