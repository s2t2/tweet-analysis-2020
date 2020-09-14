# Notes - V0

## Queries

```sql
-- TODO: create some intermediary tables to reduce query time from 6s to 1s
SELECT
  sn.user_screen_name
  ,max(sn.follower_id_count) as follower_count
  ,count(distinct t.status_id) as tweet_count
  ,sum(case when t.retweet_status_id is not null then 1 else 0 end) as rt_count
  ,count(distinct p.status_id) as prediction_count
  ,avg(p.predicted_community_id) as mean_opinion_score

FROM impeachment_production.user_screen_names_most_followed sn
JOIN impeachment_production.tweets t on upper(t.user_screen_name) = sn.user_screen_name
LEFT JOIN impeachment_production.2_community_predictions p on p.status_id = cast(t.status_id as int64)
WHERE upper(sn.user_screen_name) = upper('politico')
GROUP BY 1
-- ORDER BY 2 DESC
LIMIT 1
```
