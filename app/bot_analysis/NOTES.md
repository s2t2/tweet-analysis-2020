

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
  u.is_bot
  ,count(distinct st.user_id) as user_count
  ,count(distinct st.status_id) as status_count
  , count(st.tag) as tag_count -- 406,767
FROM impeachment_production.status_tags_v2_flat st
JOIN impeachment_production.user_details_v4 u ON u.user_id = st.user_id
WHERE st.tag in ('#QANON', '#WWG1WGA', '#GREATAWAKENING', '#WAKEUPAMERICA', '#WEARETHENEWSNOW')
GROUP BY 1
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


Prove some findings:

```sql

SELECT
 case when is_bot = true then "Bot" else "Human" end bot_status
 ,case when q_status_count > 0 then true else false end disinformation_spreader
 ,count(distinct user_id) as user_count
 ,sum(status_count) as status_count
FROM impeachment_production.user_details_vq
GROUP BY 1,2


```

```sql

SELECT
 case when is_bot = true then "Bot" else "Human" end bot_status
 --,case when q_status_count > 0 then true else false end disinformation_spreader

 ,count(distinct user_id) as user_count
 ,count(distinct case when q_status_count > 0 then user_id end) as q_user_count
 ,count(distinct case when q_status_count > 0 then user_id end) / count(distinct user_id) as q_user_pct

  -- this is the number of tweets by users who spread disinfo, not the total tweets about disinfo
 --,sum(status_count) as status_count
 --,sum(case when q_status_count > 0 then status_count end) as q_status_count
 --,sum(case when q_status_count > 0 then status_count end) / sum(status_count) as q_status_pct

FROM impeachment_production.user_details_vq
GROUP BY 1
```



Formalize the q users table:

```sql
DROP TABLE IF EXISTS impeachment_production.q_users;
CREATE TABLE IF NOT EXISTS impeachment_production.q_users as (
  SELECT
    user_id
    ,count(distinct status_id) as q_status_count
    ,count(tag) as q_tag_count
  FROM impeachment_production.status_tags_v2_flat
  WHERE tag in ('#QANON', '#WWG1WGA', '#GREATAWAKENING', '#WAKEUPAMERICA', '#WEARETHENEWSNOW')
  GROUP BY 1
)
```

Who were biggest disinfo spreaders?

```sql
-- who are the biggest spreaders?

SELECT qu.user_id ,qu.q_status_count ,qu.q_tag_count
 ,ud.screen_names
FROM impeachment_production.q_users qu -- 33,923
LEFT JOIN impeachment_production.user_details_v4 ud on ud.user_id = qu.user_id
WHERE qu.q_status_count > 1 -- 15,323
ORDER BY qu.q_status_count DESC
LIMIT 1000
```


How many q bots vs humans? 1 vs 0 opinion?

```sql
SELECT
  count(distinct qu.user_id) as q_user_count
  ,count(distinct case when is_bot=True then qu.user_id end) as q_bot_count
  ,count(distinct case when is_bot=False then qu.user_id end) as q_human_count
  ,count(distinct case when coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) < 0.5 then qu.user_id end) as opinion0
  ,count(distinct case when coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) > 0.5 then qu.user_id end) as opinion1

FROM impeachment_production.q_users qu
LEFT JOIN impeachment_production.user_details_v4 ud on ud.user_id = qu.user_id


```





























## Bot Opinion Communities

Out of 21K bots, 10K have anti-Trump opinions and 14K have pro-Trump opinions.

```sql
SELECT
--u.user_id -- ,u.user_created_at ,u.screen_name_count ,u.screen_name
--  ,u.is_bot ,u.community_id as bot_network_id
--  ,u.status_count ,u.rt_count
--  ,u.avg_score_lr ,u.avg_score_nb ,u.avg_score_bert


    --,count(distinct case when avg_score_lr = 0.5 then u.user_id end) as lr_mid
  --,count(distinct case when avg_score_nb = 0.5 then u.user_id end) as nb_mid
  --,count(distinct case when avg_score_bert = 0.5 then u.user_id end) as bert_mid -- 0

  count(distinct case when avg_score_lr is not null then u.user_id end) as lr_bots
  ,count(distinct case when avg_score_lr < 0.5 then u.user_id end) as lr_0
  ,count(distinct case when avg_score_lr > 0.5 then u.user_id end) as lr_1

  ,count(distinct case when avg_score_nb is not null then u.user_id end) as nb_bots
  ,count(distinct case when avg_score_nb < 0.5 then u.user_id end) as nb_0
  ,count(distinct case when avg_score_nb > 0.5 then u.user_id end) as nb_1

  ,count(distinct case when avg_score_bert is not null then u.user_id end) as bert_bots
  ,count(distinct case when avg_score_bert < 0.5 then u.user_id end) as bert_0
  ,count(distinct case when avg_score_bert > 0.5 then u.user_id end) as bert_1

FROM impeachment_production.user_details_v4 u
WHERE u.is_bot = true
--LIMIT 10
```

Users most retweeted by bot opinion community (upload as "users_most_retweeted_opinion_community_X.csv"):


```sql
SELECT
  rt.retweeted_user_id
  ,rt.retweeted_user_screen_name
  ,count(distinct rt.user_id) as retweeter_count
  ,count(distinct rt.status_id) as retweet_count

FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.user_details_v4 bu ON bu.user_id = rt.user_id
WHERE is_bot = true
  and avg_score_bert < 0.5 -- 10,114
  --and avg_score_bert > 0.5 -- 13,929
GROUP BY 1,2
ORDER BY 4 DESC
LIMIT 1000
```



Statuses most retweeted by bot opinion community (upload as "statuses_most_retweeted_opinion_community_X.csv"):


```sql
SELECT
  rt.status_text
  ,count(distinct rt.user_id) as retweeter_count
  ,count(distinct rt.status_id) as retweet_count

FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.user_details_v4 bu ON bu.user_id = rt.user_id
WHERE is_bot = true
  --and avg_score_bert < 0.5 -- 10,114
  and avg_score_bert > 0.5 -- 13,929
GROUP BY 1
ORDER BY 3 DESC
LIMIT 1000
```


Top status tags by bot opinion community (upload as "top_status_tags_opinion_community_X.csv"):

```sql
SELECT
  st.tag
  ,count(distinct st.user_id) as bot_count
  ,count(distinct st.status_id) as status_count

FROM impeachment_production.user_details_v4 bu
JOIN impeachment_production.status_tags_v2_flat st ON bu.user_id = st.user_id
WHERE is_bot = true
  and avg_score_bert < 0.5 -- 10,114
  --and avg_score_bert > 0.5 -- 13,929
GROUP BY 1
ORDER BY 3 DESC
LIMIT 1000
```

















(migrate profile tags flattened... )

```sql
DROP TABLE IF EXISTS impeachment_production.user_profiles_v2;
CREATE TABLE impeachment_production.user_profiles_v2 as (
  SELECT
      cast(t.user_id as int64) as user_id
      ,COALESCE(STRING_AGG(DISTINCT upper(t.user_description), ' | ') , "")   as descriptions
  FROM impeachment_production.tweets t
  GROUP BY 1
)
```

```sql
DROP TABLE IF EXISTS impeachment_production.profile_tags_v2;
CREATE TABLE impeachment_production.profile_tags_v2 as (
  SELECT
    user_id
    ,REGEXP_EXTRACT_ALL(upper(p.descriptions), r'#[A-Z0-9]+') as tags
  FROM impeachment_production.user_profiles_v2 p
  WHERE REGEXP_CONTAINS(p.descriptions, '#')
  --LIMIT 10
)
```

```sql
DROP TABLE IF EXISTS impeachment_production.profile_tags_v2_flat;
CREATE TABLE IF NOT EXISTS impeachment_production.profile_tags_v2_flat as (
    SELECT user_id, tag
    FROM impeachment_production.profile_tags_v2
    CROSS JOIN UNNEST(tags) AS tag
    -- LIMIT 10
)
```

Top profile tags by bot opinion community (upload as "top_profile_tags_opinion_community_X.csv"):

```sql
SELECT
  pt.tag
  ,count(distinct pt.user_id) as bot_count

FROM impeachment_production.user_details_v4 bu
JOIN impeachment_production.profile_tags_v2_flat pt ON bu.user_id = pt.user_id
WHERE is_bot = true
  and avg_score_bert < 0.5 -- 10,114
  --and avg_score_bert > 0.5 -- 13,929
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1000
```


















## Bot Network Communities

> Re-doing, for comprehensiveness

Users most retweeted by bot network (upload as "users_most_retweeted_network_X.csv"):


```sql
SELECT
  rt.retweeted_user_id
  ,rt.retweeted_user_screen_name
  ,count(distinct rt.user_id) as retweeter_count
  ,count(distinct rt.status_id) as retweet_count

FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.user_details_v4 bu ON bu.user_id = rt.user_id
WHERE is_bot = true
  and community_id = 0
  --and community_id = 1
GROUP BY 1,2
ORDER BY 4 DESC
LIMIT 1000
```



Statuses most retweeted by bot network (upload as "statuses_most_retweeted_network_X.csv"):


```sql
SELECT
  rt.status_text
  ,count(distinct rt.user_id) as retweeter_count
  ,count(distinct rt.status_id) as retweet_count

FROM impeachment_production.retweets_v2 rt
JOIN impeachment_production.user_details_v4 bu ON bu.user_id = rt.user_id
WHERE is_bot = true
  and community_id = 0
  --and community_id = 1
GROUP BY 1
ORDER BY 3 DESC
LIMIT 1000
```


Top status tags by bot network (upload as "top_status_tags_network_X.csv"):

```sql
SELECT
  st.tag
  ,count(distinct st.user_id) as bot_count
  ,count(distinct st.status_id) as status_count

FROM impeachment_production.user_details_v4 bu
JOIN impeachment_production.status_tags_v2_flat st ON bu.user_id = st.user_id
WHERE is_bot = true
  and community_id = 0
  --and community_id = 1
GROUP BY 1
ORDER BY 3 DESC
LIMIT 1000
```

Top profile tags by bot network (upload as "top_profile_tags_network_X.csv"):

```sql
SELECT
  pt.tag
  ,count(distinct pt.user_id) as bot_count

FROM impeachment_production.user_details_v4 bu
JOIN impeachment_production.profile_tags_v2_flat pt ON bu.user_id = pt.user_id
WHERE is_bot = true
  and community_id = 0
  --and community_id = 1
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1000
```


## Reconcile Impact Assessments

```sql

  SELECT

    count(distinct t.user_id) as total_users
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.user_id END) as humans_0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.user_id END) as humans_1
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.user_id END) as bots_0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.user_id END) as bots_1

    ,count(distinct t.status_id ) as total_tweets
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.status_id END) as human_tweets_0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.status_id END) as human_tweets_1
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.status_id END) as bot_tweets_0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.status_id END) as bot_tweets_1

    ,count(distinct CASE WHEN t.retweet_status_id IS NOT NULL THEN t.status_id END) as total_retweets
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as bot_retweets_0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as bot_retweets_1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as human_retweets_0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as human_retweets_1

  FROM impeachment_production.tweets t
  --JOIN impeachment_production.2_bot_communities bu ON bu.user_id = cast(t.user_id as int64)
  JOIN impeachment_production.user_details_v4 u ON u.user_id = cast(t.user_id as int64)
  WHERE t.created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59'
    --and u.is_bot = true
    and u.avg_score_bert is not null
```

## Bot vs Human by Opinion Community

Figures for the paper (Daily Activity Metrics).

If you want to differentiate rts from tweets:

```sql
SELECT
    extract(date from t.created_at) as date

    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.user_id END) as users_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.user_id END) as users_b1
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NULL THEN t.status_id END) as tweets_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NULL THEN t.status_id END) as tweets_b1
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as retweets_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as retweets_b1

    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.user_id END) as users_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.user_id END) as users_h1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NULL THEN t.status_id END) as tweets_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NULL THEN t.status_id END) as tweets_h1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as retweets_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 AND t.retweet_status_id IS NOT NULL THEN t.status_id END) as retweets_h1

  FROM impeachment_production.tweets t
  JOIN impeachment_production.user_details_v4 u ON u.user_id = cast(t.user_id as int64)
  WHERE t.created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59'
    and u.avg_score_bert is not null
  GROUP BY 1
  ORDER BY 1

```


Use this one:

```sql
SELECT
    extract(date from t.created_at) as date

    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.user_id END) as users_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.user_id END) as users_b1
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.status_id END) as tweets_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.status_id END) as tweets_b1

    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.user_id END) as users_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.user_id END) as users_h1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.status_id END) as tweets_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.status_id END) as tweets_h1

  FROM impeachment_production.tweets t
  JOIN impeachment_production.user_details_v4 u ON u.user_id = cast(t.user_id as int64)
  WHERE t.created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59'
    and u.avg_score_bert is not null
  GROUP BY 1
  ORDER BY 1
```


```sql
SELECT
    extract(date from t.created_at) as date

    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.user_id END) as users_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.user_id END) as users_b1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.user_id END) as users_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.user_id END) as users_h1

    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN t.status_id END) as tweets_b0
    ,count(distinct CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN t.status_id END) as tweets_b1
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN t.status_id END) as tweets_h0
    ,count(distinct CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN t.status_id END) as tweets_h1

    ,sum(CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN u.follower_count END) as  follower_reach_b0
    ,sum(CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN u.follower_count END) as  follower_reach_b1
    ,sum(CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN u.follower_count END) as follower_reach_h0
    ,sum(CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN u.follower_count END) as follower_reach_h1

    ,sum(CASE WHEN u.is_bot = true and u.avg_score_bert < 0.5 THEN u.follower_count_h END) as  human_follower_reach_b0
    ,sum(CASE WHEN u.is_bot = true and u.avg_score_bert > 0.5 THEN u.follower_count_h END) as  human_follower_reach_b1
    ,sum(CASE WHEN u.is_bot = false and u.avg_score_bert < 0.5 THEN u.follower_count_h END) as human_follower_reach_h0
    ,sum(CASE WHEN u.is_bot = false and u.avg_score_bert > 0.5 THEN u.follower_count_h END) as human_follower_reach_h1

  FROM impeachment_production.tweets t
  JOIN impeachment_production.user_details_v5 u ON u.user_id = cast(t.user_id as int64)
  WHERE t.created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59'
    and u.avg_score_bert is not null
  GROUP BY 1
  ORDER BY 1
```

## Disinfo Campaigns (Q Users) - v2

We may have some false positives in the original `q_users` table, so we're going to see if we can drop some based on their also mentioning some left-leaning tags. This would mean we have to also drop left-leaning users from the q users. They only comprise 3% of the total universe of q users. Maybe we can keep them in the table, for reference, but add some filter conditions in the dataframe that we export to CSV.

```sql
SELECT distinct tag, count(tag) as freq
FROM impeachment_production.status_tags_v2_flat
where user_id = 36690283 -- false positive q
group by 1
order by 2 desc
limit 100
```


```sql
SELECT distinct hashtag
FROM impeachment_production.2_community_tags
WHERE community_id = 0
```

```sql
WITH tags0 as (
  SELECT distinct hashtag as tag
  FROM impeachment_production.2_community_tags
  WHERE community_id = 0
  ORDER BY 1
)

SELECT
  tags0.tag
  , count(distinct user_id) as user_count
  ,count(distinct status_id) as status_count
FROM tags0
LEFT JOIN impeachment_production.status_tags_v2_flat st ON st.tag = tags0.tag
GROUP BY 1
ORDER BY 2 desc

```

Filter out users who used any left tags, or whose opinion was left:

```sql
DROP TABLE IF EXISTS impeachment_production.q_users_v2;
CREATE TABLE IF NOT EXISTS impeachment_production.q_users_v2 as (
  SELECT
    qu.user_id
    ,qu.q_status_count
    ,qu.q_tag_count
    --,count(distinct tags0.tag) as t0_count
  FROM impeachment_production.q_users qu
  LEFT JOIN impeachment_production.status_tags_v2_flat st ON qu.user_id = st.user_id --ON st.tag = tags0.tag
  LEFT JOIN (
    SELECT distinct hashtag as tag
    FROM impeachment_production.2_community_tags
    WHERE community_id = 0
    ORDER BY 1
  ) tags0 ON st.tag = tags0.tag
  LEFT JOIN impeachment_production.user_details_v4 ud on ud.user_id = qu.user_id
  WHERE coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) > 0.5
  GROUP BY 1, 2, 3
  HAVING count(distinct tags0.tag) = 0 -- out of 33.9K q users, 25.8K are pure q
  ORDER BY 2 desc
)
```

### Creation Spikes


```sql
WITH user_opinions as (
  SELECT
    user_id
    ,created_on
    ,coalesce(avg_score_bert, avg_score_nb, avg_score_lr) as opinion_score
  FROM impeachment_production.user_details_v6_slim
)

-- are the spike users more polarized?
SELECT
  if(created_on BETWEEN '2017-01-01' AND '2017-01-31', true, false) as is_spiked
  ,count(distinct user_id) as user_count
  ,count(distinct case when opinion_score < 0.5 then user_id end) as users_opinion_0
  ,count(distinct case when opinion_score > 0.5 then user_id end) as users_opinion_1
  ,round(avg(case when opinion_score < 0.5 then opinion_score end),4) as avg_opinion_0
  ,round(avg(case when opinion_score > 0.5 then opinion_score end),4) as avg_opinion_1
FROM user_opinions
GROUP BY 1

```

```sql
WITH user_opinions as (
  SELECT
    user_id
    ,created_on
    ,coalesce(avg_score_bert, avg_score_nb, avg_score_lr) as opinion_score
    ,opinion_community
  FROM impeachment_production.user_details_v6_slim
)

---- are the spike users more polarized?
--SELECT
--  if(created_on BETWEEN '2017-01-01' AND '2017-01-31', true, false) as is_spiked
--  ,opinion_community
--  ,count(distinct user_id) as user_count
--  ,round(avg(opinion_score),4) as avg_opinion
--FROM user_opinions
--GROUP BY 1,2

SELECT
  user_id
  ,if(created_on BETWEEN '2017-01-01' AND '2017-01-31', true, false) as is_spiked
  ,opinion_score
FROM user_opinions


```

Save to drive as "user_details_v6/all_users_creation_spike_opinions.csv".


### Adding Q Lookup to Daily Nodes CSV Files

```sql
SELECT user_id, screen_names, is_q, q_status_count
FROM impeachment_production.user_details_v6_slim
```

Export to drive as "user_details_v6/q_user_lookups.csv"


## Tweet Details

```sql
DROP TABLE IF EXISTS impeachment_production.tweet_details_v6;
CREATE TABLE IF NOT EXISTS impeachment_production.tweet_details_v6 as (
SELECT
  u.user_id
  ,u.screen_name_count
  ,u.screen_names
  ,u.created_on
  ,u.is_bot
  ,u.is_q
  ,if(created_on BETWEEN '2017-01-01' AND '2017-01-31', true, false) as is_spiked

  ,u.opinion_community

  ,cast(t.status_id as int64) as status_id
  ,case when t.retweet_status_id IS NULL then true else false end is_rt
  ,case when t.retweet_status_id is not null
    then upper(split(SPLIT(status_text, "@")[OFFSET(1)], ":")[OFFSET(0)])  end rt_user_sn
  ,t.status_text
  ,t.created_at
FROM impeachment_production.user_details_v6_slim u
JOIN impeachment_production.tweets t on cast(t.user_id as int64) = u.user_id
WHERE u.created_on <> '1970-01-01'
-- LIMIT 10
)
```



```sh
LIMIT=1000 BATCH_SIZE=100 DESTRUCTIVE=true python -m app.bot_analysis.download_tweet_details_v6
```



















## Daily Bot Followers

Re-do daily bots vs human follower counts.

Helper tables to shrink everything so the final query can maybe complete...


Bot followers:

```sql
DROP TABLE IF EXISTS impeachment_production.active_bot_followers_flat_v2;
CREATE TABLE IF NOT EXISTS impeachment_production.active_bot_followers_flat_v2 as (
  -- ACTIVE USERS WHO FOLLOW BOTS
  SELECT auff.user_id as bot_id ,auff.follower_id ,fu.is_bot as follower_is_bot
  FROM impeachment_production.active_followers_flat_v2 auff
  JOIN impeachment_production.user_details_v6_full u ON u.user_id = auff.user_id
  JOIN impeachment_production.user_details_v6_full fu ON fu.user_id = auff.follower_id
  WHERE u.is_Bot=True and u.opinion_community is not null
  --LIMIT 10
)
```

Shorter and slimmer user details table just for bots:

```sql
--DROP TABLE IF EXISTS impeachment_production.bot_details_v6_full;
--CREATE TABLE IF NOT EXISTS impeachment_production.bot_details_v6_full as (
--  SELECT u.*
--  FROM impeachment_production.user_details_v6_full u
--  WHERE u.is_bot=True and u.opinion_community is not null
--)

DROP TABLE IF EXISTS impeachment_production.bot_details_v6_slim;
CREATE TABLE IF NOT EXISTS impeachment_production.bot_details_v6_slim as (
  SELECT user_id
    ,created_on
    ,screen_name_count,screen_names
    ,is_bot ,bot_rt_network
    ,is_q ,q_status_count
    ,status_count ,rt_count
    ,opinion_community
    ,follower_count ,follower_count_b ,follower_count_h
    ,friend_count,friend_count_b ,friend_count_h
  FROM impeachment_production.user_details_v6_slim
  WHERE is_bot=True and opinion_community is not null
)

```

Bot tweets:

```sql
DROP TABLE IF EXISTS impeachment_production.bot_tweets;
CREATE TABLE IF NOT EXISTS impeachment_production.bot_tweets as (
  -- ACTIVE USERS WHO FOLLOW BOTS
  SELECT
    bu.user_id as bot_id
    ,cast(t.status_id as int64) as status_id
    ,cast(t.retweet_status_id as int64) as rt_status_id
    ,t.created_at
    ,t.status_text
  FROM impeachment_production.bot_details_v6_full bu
  JOIN impeachment_production.tweets t ON cast(t.user_id as int64) = bu.user_id
  WHERE bt.created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59'
)
```

Daily Active bots:

```sql
DROP TABLE IF EXISTS impeachment_production.daily_active_bots;
CREATE TABLE IF NOT EXISTS impeachment_production.daily_active_bots as (
  SELECT
    extract(date from bt.created_at) as date
    ,bt.bot_id as bot_id
  FROM impeachment_production.bot_tweets bt
  GROUP BY 1,2
)
```




Daily bot activity counts (final query):

```sql
DROP TABLE IF EXISTS impeachment_production.daily_bot_follower_counts;
CREATE TABLE IF NOT EXISTS impeachment_production.daily_bot_follower_counts as (
    WITH bots_slim as (
        SELECT user_id, opinion_community
        FROM impeachment_production.bot_details_v6_slim bu
    )

    SELECT
        dab.date

        ,count(distinct CASE WHEN bu.opinion_community=0 THEN dab.bot_id END) as users_b0
        ,count(distinct CASE WHEN bu.opinion_community=1 THEN dab.bot_id END) as users_b1
        ,count(distinct CASE WHEN bu.opinion_community=0 THEN bfl.follower_id END) as followers_b0
        ,count(distinct CASE WHEN bu.opinion_community=1 THEN bfl.follower_id END) as followers_b1

        ,count(distinct CASE WHEN bu.opinion_community=0 and bfl.follower_is_bot=false THEN bfl.follower_id END) as human_followers_b0
        ,count(distinct CASE WHEN bu.opinion_community=1 and bfl.follower_is_bot=false then bfl.follower_id END) as human_followers_b1
        ,count(distinct CASE WHEN bu.opinion_community=0 and bfl.follower_is_bot=true THEN bfl.follower_id END) as bot_followers_b0
        ,count(distinct CASE WHEN bu.opinion_community=1 and bfl.follower_is_bot=true then bfl.follower_id END) as bot_followers_b1

    FROM bots_slim bu
    JOIN impeachment_production.daily_active_bots dab ON dab.bot_id = bu.user_id
    LEFT JOIN impeachment_production.active_bot_followers_flat_v2 bfl ON dab.bot_id = bfl.bot_id
    GROUP BY 1
    -- ORDER BY 1
)
```

## Follower Venn Diagrams

```sql
-- for each follower, are they a follower of bot0? bot1? neither? both?
-- how many users of each kind does each follower follow?
-- we have to know whether the user they follow is bot or not

--SELECT
-- uff.user_id ,uff.screen_name
-- ,u.is_bot as user_is_bot
-- ,u.opinion_community as user_opinion
-- ,uff.follower_id ,uff.follower_name
--FROM impeachment_production.user_followers_flat_v2 uff
--JOIN impeachment_production.user_details_v6_slim u on u.user_id = uff.user_id
--LIMIT 10


-- how many users of each kind does each follower follow?
DROP TABLE IF EXISTS impeachment_production.active_follower_friend_counts;
CREATE TABLE IF NOT EXISTS impeachment_production.active_follower_friend_counts as (
  SELECT
    uff.follower_id ,uff.follower_name
    ,count(distinct uff.user_id) as friend_count

    ,count(distinct case when u.is_bot=True then uff.user_id end) as bot_friend_count
    ,count(distinct case when u.is_bot=False then uff.user_id end) as human_friend_count

    ,count(distinct case when u.opinion_community=0 then uff.user_id end) as opinion_1_friend_count
    ,count(distinct case when u.opinion_community=1 then uff.user_id end) as opinion_0_friend_count

    ,count(distinct case when u.is_bot=True and u.opinion_community=0 then uff.user_id end) as b0_friend_count
    ,count(distinct case when u.is_bot=True and u.opinion_community=1 then uff.user_id end) as b1_friend_count
    ,count(distinct case when u.is_bot=False and u.opinion_community=0 then uff.user_id end) as h0_friend_count
    ,count(distinct case when u.is_bot=False and u.opinion_community=1 then uff.user_id end) as h1_friend_count

  FROM impeachment_production.active_followers_flat_v2 uff
  JOIN impeachment_production.user_details_v6_slim u on u.user_id = uff.user_id
  GROUP BY 1,2

)

```
