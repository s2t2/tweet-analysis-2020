# Notes

## Queries

```sql
/*
SELECT *
FROM impeachment_production.user_friends_flat
LIMIT 10
*/


/*
SELECT
   count(distinct status_id) as status_count -- 67666557
   ,count(distinct user_id) as user_count -- 3600545
FROM impeachment_production.statuses


*/

/*
SELECT min(created_at), max(created_at) -- user_id, created_at
FROM impeachment_production.statuses
WHERE EXTRACT(DATE FROM created_at) = "2020-02-06"
-- ORDER BY created_at desc -- 2020-02-05 00:00:00
LIMIT 10
*/


SELECT DISTINCT cast(user_id as int64) as user_id, upper(user_screen_name) as user_screen_name
FROM impeachment_production.tweets
WHERE EXTRACT(DATE FROM created_at) = "2020-02-05" -- 376,224

```


```sql
SELECT
  t.status_id
  ,t.created_at
  ,t.user_id
  ,upper(t.user_screen_name) as user_screen_name
  ,uf.friend_count
  ,uf.friend_names
FROM impeachment_production.user_friends uf
JOIN impeachment_production.tweets t ON upper(t.user_screen_name) = upper(uf.screen_name)
WHERE EXTRACT(DATE FROM t.created_at) = "2020-02-05"
-- LIMIT 10

-- 53.6 sec elapsed, 27.7 GB processed
```

```sql
SELECT
  EXTRACT(DATE FROM created_at) as date
  ,count(distinct user_id) as user_count
FROM impeachment_production.tweets
GROUP BY 1
ORDER BY 1
```

## BQ Migrations

Bad migrations:

```sql
/*
DROP TABLE IF EXISTS impeachment_production.user_friends_flat_20200205;
CREATE TABLE impeachment_production.user_friends_flat_20200205 as (
  SELECT
    DISTINCT uff.screen_name, uff.friend_name
  FROM impeachment_production.user_friends_flat uff
  JOIN impeachment_production.tweets t ON t.user_id = uff.user_id
  WHERE EXTRACT(DATE FROM t.created_at) = "2020-02-05"
  -- LIMIT 10
)


SELECT count(screen_name) as row_count
FROM impeachment_production.user_friends_flat_20200205
-- 322,144,795 edges on this day

*/


/*
DROP TABLE IF EXISTS impeachment_production.user_friends_20200205;
CREATE TABLE impeachment_production.user_friends_20200205 as (

  SELECT
    uf.screen_name
    ,uf.friend_names
  FROM impeachment_production.user_friends uf
  JOIN impeachment_production.statuses t on t.user_id = uf.user_id
  WHERE uf.friend_count > 0
    AND extract(date from t.created_at) = "2020-02-05"

);
-- 1,031,392
```

Do it right:

``` sql
DROP TABLE IF EXISTS impeachment_production.user_friends_v2;
CREATE TABLE impeachment_production.user_friends_v2 as (
  SELECT
    uff.user_id
    ,uff.screen_name
    --,uff.friend_name
    ,ARRAY_AGG(DISTINCT UPPER(uff.friend_name) IGNORE NULLS) as friend_names
  FROM impeachment_production.user_friends_flat uff
  GROUP BY 1,2
);
```


```sql
DROP TABLE IF EXISTS impeachment_production.user_friends_20200205;
CREATE TABLE impeachment_production.user_friends_20200205 as (
  SELECT uf.user_id ,uf.screen_name ,uf.friend_names
  FROM impeachment_production.user_friends_v2 uf
  JOIN (
    SELECT DISTINCT user_id FROM impeachment_production.tweets t
    WHERE extract(date from t.created_at) = "2020-02-05"
  ) t ON t.user_id = uf.user_id
);

/*
SELECT count(screen_name) as row_count, sum(array_length(friend_names)) as edge_count
FROM impeachment_production.user_friends_20200205
-- 361,505
-- 322,146,064
*/
```



```sql
--SELECT REGEXP_REPLACE("RT @YoMama: Hey blah blah 456789 &^ #tag #topic. You know?", r"[^a-zA-Z0-9 @#]", "")
-- should equal 'RT @YoMama Hey blah blah 456789  #tag #topic You know'

SELECT
  REGEXP_REPLACE("RT @YoMama: Hey blah blah 456789 &^ #tag #topic. You know?", r"[^a-zA-Z0-9 @#]", "")
  ,SPLIT(UPPER(REGEXP_REPLACE("RT @YoMama: Hey blah blah 456789 &^ #tag #topic. You know?", r"[^a-zA-Z0-9 @#]", "")) , ' ') as tokens
```




```sql

  SELECT DISTINCT
    t.user_id
    -- ,ct.community_id
    -- ,count(distinct ct.hashtag) as community_score
  FROM (
    SELECT
      status_id
      ,user_id
      ,SPLIT(UPPER(REGEXP_REPLACE(status_text, r"[^a-zA-Z0-9 @#]", "")) , ' ') as tweet_tokens
    FROM impeachment_production.statuses
    WHERE status_text like '%#%'
      AND EXTRACT(DATE FROM created_at) = '2020-02-05'
    -- LIMIT 10
  ) t
  JOIN impeachment_production.2_community_tags ct ON ct.hashtag in UNNEST(t.tweet_tokens)
  WHERE ct.community_id = 1
  --GROUP BY 1,2
  --ORDER BY 1
  LIMIT 10
-- );

```

```sql
DROP TABLE IF EXISTS impeachment_production.community_0_20200205;
CREATE TABLE impeachment_production.community_0_20200205 as (

  SELECT DISTINCT t.user_id
  FROM impeachment_production.2_community_tags ct
  JOIN (
    SELECT
      status_id
      ,user_id
      ,SPLIT(UPPER(REGEXP_REPLACE(status_text, r"[^a-zA-Z0-9 @#]", "")) , ' ') as tweet_tokens
    FROM impeachment_production.statuses
    WHERE status_text like '%#%'
      AND EXTRACT(DATE FROM created_at) = '2020-02-05'
    -- LIMIT 10
  ) t ON ct.hashtag in UNNEST(t.tweet_tokens)
  WHERE ct.community_id = 0
  -- LIMIT 10
);

```

```sql
DROP TABLE IF EXISTS impeachment_production.community_1_20200205;
CREATE TABLE impeachment_production.community_1_20200205 as (

  SELECT DISTINCT t.user_id
  FROM impeachment_production.2_community_tags ct
  JOIN (
    SELECT
      status_id
      ,user_id
      ,SPLIT(UPPER(REGEXP_REPLACE(status_text, r"[^a-zA-Z0-9 @#]", "")) , ' ') as tweet_tokens
    FROM impeachment_production.statuses
    WHERE status_text like '%#%'
      AND EXTRACT(DATE FROM created_at) = '2020-02-05'
    -- LIMIT 10
  ) t ON ct.hashtag in UNNEST(t.tweet_tokens)
  WHERE ct.community_id = 1
  -- LIMIT 10
);
```


```sql

/*
SELECT count(distinct user_id) as user_count -- 6417
  FROM impeachment_production.community_1_20200205 u
  LIMIT 10
  */



DROP TABLE IF EXISTS impeachment_production.community_0_friends_20200205;
CREATE TABLE impeachment_production.community_0_friends_20200205 as (
  SELECT u.user_id, uf.screen_name, uf.friend_names
  FROM impeachment_production.community_0_20200205 u
  JOIN impeachment_production.user_friends_v2 uf ON uf.user_id = u.user_id
  -- LIMIT 10
);


DROP TABLE IF EXISTS impeachment_production.community_1_friends_20200205;
CREATE TABLE impeachment_production.community_1_friends_20200205 as (
  SELECT u.user_id, uf.screen_name, uf.friend_names
  FROM impeachment_production.community_1_20200205 u
  JOIN impeachment_production.user_friends_v2 uf ON uf.user_id = u.user_id
  -- LIMIT 10
);

```

















## PG Migrations

```sql

DROP TABLE IF EXISTS user_friends_20200205;
CREATE TABLE user_friends_20200205 as (

  SELECT
    t.user_screen_name as screen_name
    ,uf.friend_names
  FROM user_friends uf
  JOIN tweets t ON upper(t.user_screen_name) = upper(uf.screen_name)
  WHERE t.created_at::date = '2020-02-05'
    AND uf.friend_count > 0
  -- LIMIT 10
)
```


```sql
SELECT count(screen_name) as row_count
FROM user_friends_20200205
-- 998,295 tweeters
```
