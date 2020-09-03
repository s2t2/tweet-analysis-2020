# Notes

## Queries

Amazing insightful table of users most followed:

```sql
SELECT
    uff.friend_name as user_screen_name
    ,count(distinct uff.user_id) as follower_id_count
    ,count(distinct uff.screen_name) as follower_screen_name_count
FROM impeachment_production.user_friends_flat uff
group by 1
order by 2 desc
-- 117,437,748 rows
```

```sql
SELECT count(distinct user_screen_name) as user_sn_count
FROM (
    SELECT
        sn.user_id -- lots of nulls
        ,uff.friend_name as user_screen_name
        ,uff.user_id as follower_id
        ,uff.screen_name as follower_screen_name
    FROM impeachment_production.user_friends_flat uff
    LEFT JOIN impeachment_production.user_screen_names sn ON sn.screen_name = uff.friend_name
    -- WHERE sn.user_id is null -- 114,450,235
    -- WHERE sn.user_id is not null -- 2,987,513
) -- gotta make these graphs using screen names I think or run an id lookup pass on them...
```

## Migrations

```sql
DROP TABLE IF EXISTS impeachment_production.user_followers;
CREATE TABLE impeachment_production.user_followers as (
    SELECT
        sn.user_id -- lots of nulls
        ,uff.friend_name as user_screen_name
        ,uff.user_id as follower_id
        ,uff.screen_name as follower_screen_name
    FROM impeachment_production.user_friends_flat uff
    LEFT JOIN impeachment_production.user_screen_names sn ON sn.screen_name = uff.friend_name
);
```

```sql
DROP TABLE IF EXISTS impeachment_production.user_follower_lists;
CREATE TABLE impeachment_production.user_follower_lists as (
    SELECT
        user_screen_name
        ,ARRAY_LENGTH(follower_screen_names) as follower_count
        ,follower_screen_names
    FROM (
        SELECT
            user_screen_name
            -- ,ARRAY_LENGTH(DISTINCT follower_screen_names) as follower_count -- can't use distinct here
            ,ARRAY_AGG(DISTINCT follower_screen_name) as follower_screen_names
        FROM impeachment_production.user_followers
        GROUP BY 1
    ) -- 3-4 mins for 117,437,748 distinct user screen names
);
```

## More Queries

```sql
SELECT
    uf.user_screen_name
    ,uf.follower_count
    --,uf.follower_screen_names
FROM impeachment_production.user_follower_lists uf
JOIN (
  SELECT distinct upper(rt.user_screen_name) as user_screen_name
  FROM impeachment_production.retweets rt
  WHERE rt.created_at BETWEEN '2020-01-01' AND '2020-01-02' -- 111,623 screen names
) retweeters ON retweeters.user_screen_name = uf.user_screen_name
```

```sql
SELECT distinct user_screen_name
FROM impeachment_production.user_followers uf
WHERE user_id is null
```
