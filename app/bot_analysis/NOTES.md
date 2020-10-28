



## Analysis Queries - All Bots

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

```sql
CREATE TABLE impeachment_production.bots_above_80_v2 as (
  SELECT
    dbp.user_id
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
)
```

## Analysis Queries - Bots vs Humans

### Users Most Retweeted

Users Most Retweeted:

```sql
SELECT DISTINCT
    rt.retweeted_user_id
    ,rt.retweeted_user_screen_name

    ,count(distinct rt.user_id) as retweeter_count
    ,count(distinct rt.status_id) as retweet_count

FROM impeachment_production.retweets_v2 rt
GROUP BY 1,2
ORDER BY 3 DESC
LIMIT 1000
```

Users most retweeted by bots vs non-bots:

```sql

-- users most retweeted
-- (by bots vs humans)
SELECT DISTINCT
    rt.retweeted_user_id
    ,rt.retweeted_user_screen_name

    ,count(distinct rt.user_id) as retweeter_count
    ,count(distinct rt.status_id) as retweet_count

    ,count(distinct CASE WHEN bu.user_id IS NOT NULL THEN rt.user_id END) as bot_retweeter_count
    ,count(distinct CASE WHEN bu.user_id IS NOT NULL THEN rt.status_id END) as bot_retweet_count

    ,count(distinct CASE WHEN bu.user_id IS NULL THEN rt.user_id END) as human_retweeter_count
    ,count(distinct CASE WHEN bu.user_id IS NULL THEN rt.status_id END) as human_retweet_count

FROM impeachment_production.retweets_v2 rt
LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = rt.user_id
GROUP BY 1,2
ORDER BY 3 DESC
LIMIT 1000

```

### Top Hashtags

Operating on only 6.7M tweets that likely have hashtags:

```sql
SELECT count(distinct status_id) as status_count
FROM impeachment_production.tweets
WHERE REGEXP_CONTAINS(upper(status_text), '#') -- 6,878,708
```

Prep a table of tweets with hashtags.

```sql
CREATE TABLE impeachment_production.tag_tweets as (
  SELECT cast(user_id as int64) as user_id, cast(status_id as int64) as status_id, status_text
  FROM impeachment_production.tweets
  WHERE REGEXP_CONTAINS(upper(status_text), '#') -- 6,878,708
  -- LIMIT 10
)
```

Download the table via BigQuery / GCS (JK use script below). Save locally as "data/bot_analysis/tag_tweets.csv".

Top hashtags:

```py
python -m app.bot_analysis.top_tags
```

Top hashtags used by bots vs non-bots:

```sql
```