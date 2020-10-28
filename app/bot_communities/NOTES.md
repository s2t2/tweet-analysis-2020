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
