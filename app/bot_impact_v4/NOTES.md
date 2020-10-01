# Notes

## Queries

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
