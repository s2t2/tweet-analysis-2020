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
