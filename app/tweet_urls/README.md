


```sql
SELECT count(distinct t.status_id)
FROM `tweet-collector-py.impeachment_production.tweets` t -- 67,666,557
WHERE t.retweet_status_id is null -- 11,759,296
```

```sh

```
