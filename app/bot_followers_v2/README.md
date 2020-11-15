# Bot Followers v2

For the bots, how many (active) followers does each have, and who are they?


```sql
DROP TABLE IF EXISTS impeachment_production.user_followers_v2;
CREATE TABLE impeachment_production.user_followers_v2 as (
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
DROP TABLE IF EXISTS impeachment_production.active_user_followers_v2;
CREATE TABLE impeachment_production.active_user_followers_v2 as (
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
SELECT
  count(distinct user_id) as user_count -- 2,987,137
  ,count(distinct follower_id) as follower_count -- 3,315,115
FROM impeachment_production.user_followers_v2
```

```sql
SELECT
  count(distinct user_id) as user_count -- 2,971,946
  ,count(distinct follower_id) as follower_count -- 3,310,307
FROM impeachment_production.active_user_followers_v2
```


```sql
SELECT
  count(distinct uf.user_id) as user_count -- 22,814
  , count(distinct uf.follower_id) as follower_count -- 886,275
FROM impeachment_production.user_followers_v2 uf
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
  FROM impeachment_production.user_followers_v2 uf
  JOIN impeachment_production.user_details_v4 bu on bu.user_id = uf.user_id
  WHERE bu.is_bot = true
  GROUP BY 1
)
```
