# Notes

```sql
SELECT count(distinct status_id) as status_count, count(distinct user_id) as user_count
FROM election_2020_production.tweets
```


```sql
SELECT 
extract(date from created_at) as day
,count(distinct status_id) as status_count
,count(distinct user_id) as user_count
FROM election_2020_production.tweets
GROUP BY 1
ORDER BY 1 desc
```

