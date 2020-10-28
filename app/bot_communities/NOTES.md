# Notes

## Queries


```sql
DROP TABLE IF EXISTS impeachment_production.2_community_profiles;
CREATE TABLE impeachment_production.2_community_profiles as (
  SELECT
      c.community_id
      ,b.bot_id
      -- ,b.bot_screen_name
      --,b.day_count
      --,b.avg_daily_score
      ,count(distinct t.status_id) as tweet_count
      ,COALESCE(STRING_AGG(DISTINCT upper(t.user_screen_name), ' | ') , "")   as screen_names
      ,COALESCE(STRING_AGG(DISTINCT upper(t.user_name), ' | ')        , "")   as user_names
      ,COALESCE(STRING_AGG(DISTINCT upper(t.user_description), ' | ') , "")   as user_descriptions
  FROM impeachment_production.bots_above_80 b
  JOIN impeachment_production.2_bot_communities c ON c.user_id = b.bot_id
  JOIN impeachment_production.tweets t on cast(t.user_id as int64) = b.bot_id
  GROUP BY 1,2
  ORDER BY 1,2
);
```

## Analysis Queries

Generate "all_bots_grouped_by_id_and_screen_name.csv":

```sql
SELECT -- count(distinct user_id) as user_count
  dbp.user_id
  ,sn.screen_name
  ,bu.community_id
  ,count(distinct dbp.start_date) as day_count
  , avg(dbp.bot_probability) as avg_bot_probability
FROM impeachment_production.daily_bot_probabilities dbp -- 208640
LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = dbp.user_id
LEFT JOIN impeachment_production.user_screen_names sn ON dbp.user_id = cast(sn.user_id as int64) -- 24973
WHERE dbp.bot_probability > 0.8 -- 24150
GROUP BY 1, 2,3
ORDER BY 1 -- day_count DESC

```

Generate "all_bots_grouped_by_id.csv":


```sql
SELECT -- count(distinct user_id) as user_count
  dbp.user_id
  --,sn.screen_names
  ,ud.screen_names
  ,ud.screen_name_count
  ,bu.community_id
  ,count(distinct dbp.start_date) as day_count
  , avg(dbp.bot_probability) as avg_bot_probability
FROM impeachment_production.daily_bot_probabilities dbp -- 208640
LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = dbp.user_id
LEFT JOIN impeachment_production.user_details_v3 ud ON ud.user_id = dbp.user_id
WHERE dbp.bot_probability > 0.8 -- 24150
GROUP BY 1,2,3,4
ORDER BY 3 desc

```
