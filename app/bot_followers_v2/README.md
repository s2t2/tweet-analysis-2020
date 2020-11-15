# Bot Followers v2

For the bots, how many (active) followers does each have, and who are they?

## User Followers Flat - v2


```sql
DROP TABLE IF EXISTS impeachment_production.user_followers_flat_v2;
CREATE TABLE impeachment_production.user_followers_flat_v2 as (
  SELECT
    cast(sn.user_id as int64) as user_id
    ,sn.screen_name
    ,cast(uff.user_id as int64) as follower_id
    ,uff.screen_name as follower_name
  FROM impeachment_production.user_screen_names sn
  JOIN impeachment_production.user_friends_flat uff ON upper(sn.screen_name) = upper(uff.friend_name)
  --WHERE sn.screen_name = "ACLU"
  --LIMIT 100
)
```

```sql
DROP TABLE IF EXISTS impeachment_production.active_followers_flat_v2;
CREATE TABLE impeachment_production.active_followers_flat_v2 as (
  SELECT
    cast(sn.user_id as int64) as user_id
    ,sn.screen_name
    ,cast(auff.user_id as int64) as follower_id
    ,auff.screen_name as follower_name
  FROM impeachment_production.user_screen_names sn
  JOIN impeachment_production.active_user_friends_flat auff ON upper(sn.screen_name) = upper(auff.friend_name)
  --WHERE sn.screen_name = "ACLU"
  --LIMIT 100
)
```


```sql
-- FOLLOWERS
SELECT
  count(distinct user_id) as user_count -- 2,987,137
  ,count(distinct follower_id) as follower_count -- 3,315,115
FROM impeachment_production.user_followers_flat_v2
```

```sql
-- ACTIVE FOLLOWERS
SELECT
  count(distinct user_id) as user_count -- 2,971,946
  ,count(distinct follower_id) as follower_count -- 3,310,307
FROM impeachment_production.active_followers_flat_v2
```


```sql
SELECT
  count(distinct uf.user_id) as user_count -- 22,814
  , count(distinct uf.follower_id) as follower_count -- 886,275
FROM impeachment_production.user_followers_flat_v2 uf
JOIN impeachment_production.user_details_v4 bu on bu.user_id = uf.user_id
WHERE bu.is_bot = true

```

```sql
SELECT
  count(distinct bu.user_id) as user_count -- 24,150
FROM impeachment_production.user_details_v4 bu
WHERE bu.is_bot = true
```

OK so about 1300 bots have no followers. that makes sense. For the remaining bots, how many followers on average?

```sql
SELECT
    count(distinct user_id) as bot_count -- 22814
    , round(avg(follower_count), 4) as avg_followers -- 1308.10173
FROM (
  SELECT
    uf.user_id
    , count(distinct uf.follower_id) as follower_count
  FROM impeachment_production.user_followers_flat_v2 uf
  JOIN impeachment_production.user_details_v4 bu on bu.user_id = uf.user_id
  WHERE bu.is_bot = true
  GROUP BY 1
)
```

... as compared to humans?


```sql
SELECT
    count(distinct user_id) as human_count -- 2,949,208
    ,round(avg(follower_count), 4) as avg_followers -- 207.5755
FROM (
  SELECT
    uf.user_id
    , count(distinct uf.follower_id) as follower_count
  FROM impeachment_production.user_followers_flat_v2 uf
  JOIN impeachment_production.user_details_v4 bu on bu.user_id = uf.user_id
  WHERE bu.is_bot = false
  GROUP BY 1
)
```

So bots have five times as many active followers? Let's see the bots with the most followers:


```sql
  SELECT
    uf.user_id
    ,string_agg(uf.screen_name, " | ") as screen_names
    ,count(distinct uf.follower_id) as follower_count
  FROM impeachment_production.user_followers_flat_v2 uf
  JOIN impeachment_production.user_details_v4 bu on bu.user_id = uf.user_id
  WHERE bu.is_bot = false
  GROUP BY 1
  ORDER BY follower_count desc
  LIMIT 10
```

Should we be restricting this to see how many **human** followers?

## User Followers - v2

```sql
-- for the follower:
-- ... are they bot or not?
-- ... is their opinion 0 or 1?
SELECT
  uff.user_id
  ,uff.screen_name
  ,uff.follower_id
  ,uff.follower_name
  ,CASE WHEN fbu.user_id IS NOT NULL THEN true ELSE false END follower_is_bot
FROM impeachment_production.active_followers_flat_v2 uff
LEFT JOIN impeachment_production.bots_above_80_v2 fbu ON fbu.user_id = uff.follower_id
LIMIT 10
```


```sql
-- for the follower:
-- ... are they bot or not?
-- ... is their opinion 0 or 1?

DROP TABLE IF EXISTS impeachment_production.active_followers_bh_v2;
CREATE TABLE IF NOT EXISTS impeachment_production.active_followers_bh_v2 as (
  SELECT
     user_id
     --,screen_name
    ,count(distinct follower_id) as follower_count
    --,array_agg(distinct follower_id) as follower_ids

    ,count(distinct case when follower_is_bot = true then follower_id end) as follower_count_b
    ,count(distinct case when follower_is_bot = false then follower_id end) as follower_count_h

    ,array_agg(distinct case when follower_is_bot = true then follower_id end) as follower_ids_b
    ,array_agg(distinct case when follower_is_bot = false then follower_id end) as follower_ids_h

  FROM (
    SELECT
      uff.user_id
      ,uff.screen_name
      ,uff.follower_id
      ,uff.follower_name
      ,CASE WHEN fbu.user_id IS NOT NULL THEN true ELSE false END follower_is_bot
    FROM impeachment_production.active_followers_flat_v2 uff
    LEFT JOIN impeachment_production.bots_above_80_v2 fbu ON fbu.user_id = uff.follower_id
    -- LIMIT 10
  ) zz
  GROUP BY 1
)

```
