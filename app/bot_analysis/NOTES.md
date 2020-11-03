

# Analysis Queries

## Detection All Bots

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

## Bots vs Humans

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

Prep a table of tweets with hashtags, also including a bot flag:

```sql
DROP TABLE IF EXISTS impeachment_production.statuses_with_tags;
CREATE TABLE impeachment_production.statuses_with_tags as (
  SELECT
    cast(t.user_id as int64) as user_id
    ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
    ,cast(t.status_id as int64) as status_id
    , t.status_text
  FROM impeachment_production.tweets t
  LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = cast(t.user_id as int64)
  WHERE REGEXP_CONTAINS(status_text, '#') -- 6,878,708
  --LIMIT 10
)
```

Top status hashtags (by bots vs non-bots):

```py
python -m app.bot_analysis.top_status_tags
# DESTRUCTIVE=true LIMIT=1000 BATCH_SIZE=100 python -m app.bot_analysis.top_status_tags
# APP_ENV="prodlike" python -m app.bot_analysis.top_status_tags
```

### Bots Most Active

```sql
CREATE TABLE impeachment_production.bots_most_active as (
  SELECT
    user_id
    ,user_created_at
    ,screen_name_count
    ,screen_names
    ,is_bot
    ,community_id
    ,status_count
    ,rt_count
    ,avg_score_lr
    ,avg_score_nb
    ,avg_score_bert
  FROM impeachment_production.user_details_v4
  WHERE is_bot = true
  ORDER BY status_count DESC
  LIMIT 1000
)
```

Export the top 100 to JSON and use for the website.










## Bot Network Communities

Users most retwteeted by bot community:

```sql
SELECT DISTINCT
    bu.community_id
    ,rt.retweeted_user_id
    ,rt.retweeted_user_screen_name
    ,count(distinct rt.user_id) as retweeter_count
    ,count(distinct rt.status_id) as retweet_count --
FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = rt.user_id
WHERE community_id = 0
--WHERE community_id = 1
--WHERE community_id is null
GROUP BY 1,2,3
ORDER BY 5 DESC
LIMIT 1000
```

## Bot Opinion Communities

Users most retweeted by bot opinion community:


```sql

/*
SELECT DISTINCT
    bu.community_id
    ,rt.retweeted_user_id
    ,rt.retweeted_user_screen_name
    ,count(distinct rt.user_id) as retweeter_count
    ,count(distinct rt.status_id) as retweet_count --
FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = rt.user_id
WHERE community_id is null
GROUP BY 1,2,3
ORDER BY 5 DESC
LIMIT 1000
*/

  SELECT
    --bu.user_id
    --,bu.user_created_at
    --,bu.screen_name_count
    --,bu.screen_names
    --,bu.is_bot
    --,bu.community_id
    --,status_count
    --,rt_count
    --,bu.avg_score_lr
    --,bu.avg_score_nb
    --,bu.avg_score_bert

    "Pro-Impeachment BERT" as opinion_community
    ,rt.retweeted_user_id
    ,rt.retweeted_user_screen_name
    ,count(distinct rt.user_id) as retweeter_count
    ,count(distinct rt.status_id) as retweet_count

  FROM impeachment_production.user_details_v4 bu
  JOIN impeachment_production.retweets_v2 rt ON bu.user_id = rt.user_id
  WHERE is_bot = true and avg_score_bert < 0.5 -- 10,114
  --WHERE is_bot = true and avg_score_bert > 0.5 -- 13929
  --WHERE is_bot = true and avg_score_bert = 0.5 -- 0
  GROUP BY 1,2,3
  ORDER BY 5 DESC
  LIMIT 1000


```

## Disinformation Campaigns

  + https://wt.social/post/fighting-misinformation/nvrqyhu5325591624484


Flattening a table of status hashtags. This will be the key for quick queries.

Regex tests:

```sql
SELECT
  --t.status_text,
  REGEXP_EXTRACT_ALL(t.status_text, r'#[A-Za-z0-9\-\.\_]+') as tags
FROM (
  SELECT 'RT @Rosie: trump is unfit to lead - he should be impeached for firing the Vindman brothers #VindmanIsAHero #CoronavirusOutbreak is real - #…' as status_text
) t
--> #VindmanIsAHero
--> #CoronavirusOutbreak
```

```sql
SELECT
  --t.status_text,
  REGEXP_EXTRACT_ALL(upper(t.status_text), r'#[A-Z0-9]+') as tags
FROM (
  SELECT 'RT @Rosie: trump is unfit to lead - he should be impeached for firing the Vindman brothers #VindmanIsAHero #CoronavirusOutbreak is real - #… RT @evamckend: It began with bold refusal to act as neutral party in #impeachment.  By wearing down Senators w/ grueling schedule, keeping… #impeachment-scam yo' as status_text
) t
```

```sql
SELECT
 t.user_id
 ,status_id
 ,status_text
 --,REGEXP_EXTRACT_ALL(t.status_text, r'#[A-Za-z0-9\-\.\_]+') as tags
 ,REGEXP_EXTRACT_ALL(upper(t.status_text), r'#[A-Z0-9]+') as tags
 ,REGEXP_EXTRACT_ALL(upper(t.status_text), r'@[A-Z0-9]+') as mentions
FROM impeachment_production.statuses_with_tags t
LIMIT 100
```

```sql
SELECT
 cast(t.user_id as int64) as user_id
 ,cast(t.status_id as int64) as status_id
 ,t.created_at
 ,t.status_text
 ,REGEXP_EXTRACT_ALL(upper(t.status_text), r'#[A-Z0-9]+') as tags
FROM impeachment_production.tweets t
WHERE REGEXP_CONTAINS(t.status_text, '#')
LIMIT 100
```

```sql
DROP TABLE IF EXISTS impeachment_production.status_tags_v2;
CREATE TABLE impeachment_production.status_tags_v2 as (
  SELECT
   cast(t.user_id as int64) as user_id
   ,cast(t.status_id as int64) as status_id
   --,t.created_at
   --,t.status_text
   ,REGEXP_EXTRACT_ALL(upper(t.status_text), r'#[A-Z0-9]+') as tags
  FROM impeachment_production.tweets t
  WHERE REGEXP_CONTAINS(t.status_text, '#')
  --LIMIT 10
)

DROP TABLE IF EXISTS impeachment_production.status_mentions_v2;
CREATE TABLE impeachment_production.status_mentions_v2 as (
  SELECT
   cast(t.user_id as int64) as user_id
   ,cast(t.status_id as int64) as status_id
   --,t.created_at
   --,t.status_text
   ,REGEXP_EXTRACT_ALL(upper(t.status_text), r'@[A-Z0-9]+') as mentions
  FROM impeachment_production.tweets t
  WHERE REGEXP_CONTAINS(t.status_text, '@')
  --LIMIT 10
)
```

Flattened tables for faster joining in the future:

```sql
DROP TABLE IF EXISTS impeachment_production.status_tags_v2_flat;
CREATE TABLE IF NOT EXISTS impeachment_production.status_tags_v2_flat as (
    SELECT user_id, status_id, tag
    FROM impeachment_production.status_tags_v2
    CROSS JOIN UNNEST(tags) AS tag
    -- LIMIT 10
);


DROP TABLE IF EXISTS impeachment_production.status_mentions_v2_flat;
CREATE TABLE IF NOT EXISTS impeachment_production.status_mentions_v2_flat as (
    SELECT user_id, status_id, mention
    FROM impeachment_production.status_mentions_v2
    CROSS JOIN UNNEST(mentions) AS mention
    -- LIMIT 10
)
```

```sql
-- https://wt.social/post/fighting-misinformation/nvrqyhu5325591624484
SELECT
  count(distinct user_id) as user_count -- 33,923
  ,count(distinct status_id) as status_count -- 154,031
  , count(tag) as tag_count -- 406,767
FROM impeachment_production.status_tags_v2_flat
WHERE tag in ('#QANON', '#WWG1WGA', '#GREATAWAKENING', '#WAKEUPAMERICA', '#WEARETHENEWSNOW')
```

```sql
SELECT tag
,count(distinct user_id) as user_count ,count(distinct status_id) as status_count, count(tag) as tag_count
FROM impeachment_production.status_tags_v2_flat
--WHERE user_id = 1086761984807194624
WHERE tag in ('#QANON', '#WWG1WGA', '#GREATAWAKENING', '#WAKEUPAMERICA', '#WEARETHENEWSNOW')
GROUP BY 1
ORDER BY 2 DESC
```




```sql
SELECT
  u.user_id
   --,u.user_created_at
  ,extract(date from u.user_created_at) as creation_date
  ,u.screen_name_count
  --,u.screen_names
  ,status_count
  ,rt_count
  ,u.is_bot
  ,u.community_id as bot_network_community
  ,case when avg_score_bert > 0.5 then 1 when avg_score_bert < 0.5 then 0 end opinion_community
  ,u.avg_score_lr
  ,u.avg_score_nb
  ,u.avg_score_bert


FROM impeachment_production.user_details_v4 u
--JOIN impeachment_production.bots_above_80_v2 bu ON bu.bot_id = u.user_id
LIMIT 10
```

Which bots are retweeting a specific set of disinformation topics?


```sql
DROP TABLE IF EXISTS impeachment_production.user_details_vq;
CREATE TABLE impeachment_production.user_details_vq as (

  SELECT
    u.user_id
    ,extract(date from u.user_created_at) as creation_date
    ,u.screen_name_count
    ,u.screen_names
    ,u.status_count ,u.rt_count


    ,u.is_bot
    ,u.community_id as bot_community

    --,u.avg_score_lr ,u.avg_score_nb ,u.avg_score_bert
    ,coalesce(avg_score_bert, avg_score_lr, avg_score_nb) as mean_opinion
    ,case
      when coalesce(avg_score_bert, avg_score_lr, avg_score_nb) > 0.5 then 1
      when coalesce(avg_score_bert, avg_score_lr, avg_score_nb) < 0.5 then 0
    end opinion_community


    ,coalesce(q.status_count, 0) as q_status_count
    --,q.tag_count as q_tag_count
    ,coalesce(round(q.status_count / u.status_count, 4), 0) as q_status_pct

  FROM impeachment_production.user_details_v4 u
  LEFT JOIN (
    SELECT user_id ,count(distinct status_id) as status_count, count(tag) as tag_count
    FROM impeachment_production.status_tags_v2_flat
    WHERE tag in ('#QANON', '#WWG1WGA', '#GREATAWAKENING', '#WAKEUPAMERICA', '#WEARETHENEWSNOW')
    GROUP BY 1
  ) q ON q.user_id = u.user_id
  --WHERE avg_score_bert is null and avg_score_lr is null
  --LIMIT 10
)

/*
SELECT *
FROM impeachment_production.user_details_vq -- 3,600,545
LIMIT 10
*/
```

```py
DESTRUCTIVE=true LIMIT=1000 BATCH_SIZE=100 python -m app.bot_analysis.user_details_vq

# APP_ENV="prodlike" python -m app.bot_analysis.user_details_vq
```

Export to Tableau and have some fun!
