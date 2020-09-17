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
