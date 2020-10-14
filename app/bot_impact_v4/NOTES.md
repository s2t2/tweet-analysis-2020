# Notes

## Queries

### Active User Friend Graphs

```sql
SELECT
  count(distinct status_id) as status_count
  , count(distinct CASE WHEN community_id = 0 THEN status_id END)  as status0_count
  , count(distinct CASE WHEN community_id = 1 THEN status_id END)  as status1_count

  , count(distinct user_id) as user_count
  --, count(distinct CASE WHEN bot THEN user_id END)  as bot_count
  , count(distinct CASE WHEN community_id = 0 THEN user_id END)  as user0_count
  , count(distinct CASE WHEN community_id = 1 THEN user_id END)  as user1_count
FROM (
  SELECT
      t.status_id
      , t.status_text
      , t.created_at
      , t.user_id
      , t.user_screen_name as screen_name
      ,CASE WHEN bu.community_id IS NOT NULL THEN TRUE ELSE FALSE END bot
      ,bu.community_id
  FROM impeachment_production.tweets t
  LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = cast(t.user_id as int64)
  WHERE EXTRACT(DATE from created_at) = '2020-02-05'
    -- AND bu.community_id = 0 -- 10406 | 515
    -- AND bu.community_id = 1 --
  -- LIMIT 10
)

```

```sql

  SELECT
      t.status_id
      , t.status_text
      , t.created_at
      , t.user_id
      , t.user_screen_name as screen_name
      ,CASE WHEN bu.community_id IS NOT NULL THEN TRUE ELSE FALSE END bot
      ,bu.community_id
      ,r.tweet_count as rate
  FROM impeachment_production.tweets t
  LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = cast(t.user_id as int64)
  JOIN (
    SELECT
       cast(user_id as INT64) as user_id, count(distinct status_id) as tweet_count
    FROM impeachment_production.tweets t
    WHERE EXTRACT(DATE from created_at) = '2020-01-23'
    GROUP BY 1
    -- LIMIT 10
  ) r ON r.user_id = cast(t.user_id as int64)
  WHERE EXTRACT(DATE from created_at) = '2020-01-23'
  --LIMIT 10

```

```sql
DROP TABLE IF EXISTS impeachment_production.active_user_friends_flat;
CREATE TABLE impeachment_production.active_user_friends_flat AS (
  SELECT user_id, screen_name, friend_name
  FROM impeachment_production.user_friends_flat
  WHERE screen_name in (SELECT DISTINCT upper(user_screen_name) FROM impeachment_production.tweets)
    AND friend_name in (SELECT DISTINCT upper(user_screen_name) FROM impeachment_production.tweets)
  -- LIMIT 10
); --> 642,079,860 rows (vs 1,976,670,168) so about 1/3 the size of the original uff
```

```sql
DROP TABLE IF EXISTS impeachment_production.active_user_friends;
CREATE TABLE impeachment_production.active_user_friends as (
  SELECT
    cast(uff.user_id as int64) as user_id
    ,uff.screen_name
    ,ARRAY_AGG(DISTINCT uff.friend_name) as friend_names
    ,count(DISTINCT uff.friend_name) as friend_count
  FROM impeachment_production.active_user_friends_flat uff
  GROUP BY 1,2
);
```

```sql
SELECT dau.user_id, dau.tweet_count as rate, uf.screen_name ,uf.friend_count, uf.friend_names
FROM (
    SELECT
       cast(user_id as INT64) as user_id, count(distinct status_id) as tweet_count
    FROM impeachment_production.tweets t
    WHERE EXTRACT(DATE from created_at) = '2020-01-23'
    GROUP BY 1
    LIMIT 10
) dau
JOIN impeachment_production.active_user_friends uf ON uf.user_id = dau.user_id
LIMIT 10
```

### Active Edge Friend Graphs


```sql
WITH dau AS (
  SELECT
    cast(user_id as INT64) as user_id
    , upper(user_screen_name) as screen_name
    , count(distinct status_id) as rate
  FROM impeachment_production.tweets
  WHERE EXTRACT(DATE FROM created_at) = '2020-02-05'
  GROUP BY 1,2
  HAVING count(distinct status_id) >= 3
)

SELECT
  dau.user_id
  ,dau.screen_name
  ,dau.rate
  ,uff.friend_name
FROM dau
JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = dau.user_id
WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM dau)
-- LIMIT 10
```

```sql
WITH dau AS (
  SELECT
    cast(user_id as INT64) as user_id
    , upper(user_screen_name) as screen_name
    , count(distinct status_id) as rate
  FROM impeachment_production.tweets
  WHERE EXTRACT(DATE FROM created_at) = '2020-02-05'
  GROUP BY 1,2
  HAVING count(distinct status_id) >= 2 -- 3: 96849
)

SELECT
  dau.user_id
  ,dau.screen_name
  ,dau.rate
  ,ARRAY_AGG(DISTINCT uff.friend_name) as friend_names
   ,count(DISTINCT uff.friend_name) as friend_count
FROM dau
JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = dau.user_id
WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM dau)
GROUP BY 1,2,3

-- LIMIT 10
```

Getting TZ a CSV file in desired format:

```sql
WITH dau AS (
    SELECT
        cast(user_id as INT64) as user_id
        ,upper(user_screen_name) as screen_name
        ,count(distinct status_id) as rate
    FROM impeachment_production.tweets
    WHERE EXTRACT(DATE FROM created_at) = '2020-01-23'
    GROUP BY 1,2
    HAVING count(distinct status_id) >= 2
)

SELECT
    dau.user_id
    ,dau.screen_name
    ,dau.rate
    ,STRING_AGG(DISTINCT uff.friend_name) as friend_names -- string agg so we can export to CSV
    ,count(DISTINCT uff.friend_name) as friend_count
FROM dau
JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = dau.user_id
WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM dau)
GROUP BY 1,2,3
```

Flagging duplicate statuses to be de-duped for model training and evaluation:


```sql
SELECT DISTINCT
    t.status_id
    ,t.status_text
    ,t.created_at
    ,t.user_id
    ,UPPER(t.user_screen_name) as screen_name
    ,CASE WHEN bu.community_id IS NOT NULL THEN TRUE ELSE FALSE END bot
    ,cast(bu.community_id as int64) as community_id
    ,r.tweet_count as rate
    ,st.status_count as dup_status_text_count
    ,st.status_ids as dup_status_ids
FROM impeachment_production.tweets t
LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = cast(t.user_id as int64)
JOIN (
    SELECT cast(user_id as INT64) as user_id, count(distinct status_id) as tweet_count
    FROM impeachment_production.tweets t
    WHERE EXTRACT(DATE from created_at) = '2020-01-23'
    GROUP BY 1
    -- LIMIT 10
) r ON r.user_id = cast(t.user_id as int64)
LEFT JOIN (

  SELECT
    t.status_text
    ,count(distinct t.status_id) as status_count
    ,string_agg(distinct t.status_id) as status_ids
  FROM impeachment_production.tweets t
  WHERE extract(date from t.created_at) = '2020-01-23'
  GROUP BY 1

) st ON st.status_text = t.status_text
WHERE EXTRACT(DATE from created_at) = '2020-01-23'
LIMIT 10
```

Refactor:

```sql
WITH daily_tweets AS (
  SELECT
    cast(t.user_id as int64) as user_id
    ,UPPER(t.user_screen_name) as screen_name
    ,cast(t.status_id as int64) as status_id
    ,t.status_text
    ,t.created_at
  FROM impeachment_production.tweets t
  WHERE extract(date from t.created_at) = '2020-01-23'
)

SELECT DISTINCT
    t.status_id ,t.status_text ,t.created_at
    ,t.user_id ,t.screen_name
    ,CASE WHEN bu.community_id IS NOT NULL THEN TRUE ELSE FALSE END bot
    ,cast(bu.community_id as int64) as community_id
    ,r.tweet_count as rate
    ,st.status_count as status_text_occurance
FROM daily_tweets t
LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = t.user_id
JOIN (
    SELECT cast(user_id as INT64) as user_id, count(distinct status_id) as tweet_count
    FROM daily_tweets t
    GROUP BY 1
) r ON r.user_id = cast(t.user_id as int64)
LEFT JOIN (
    SELECT t.status_text, count(distinct t.status_id) as status_count
    FROM daily_tweets t
    GROUP BY 1
) st ON st.status_text = t.status_text
LIMIT 10
```
