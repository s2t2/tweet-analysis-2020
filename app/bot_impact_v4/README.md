# Assessing Bot Impact

## Daily Active User Friend Graphs

We are looking at all users who tweeted (at least X times) on a given day. We're assembling graphs for each of them and each of the people they follow who are also tweeting about impeachment (at some time, or on that same day, respectively):

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_user_friend_grapher
```

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_edge_friend_grapher
```

## For Real Though (v5)


JK JK, we're going to dynamically find the tweet min, and we also want to include tweet opinion scores:

```sh
START_DATE="2019-12-20" N_PERIODS=60 python -m app.bot_impact_v4.daily_active_edge_downloader

APP_ENV="prodlike" START_DATE="2020-01-08" N_PERIODS=40 python -m app.bot_impact_v4.daily_active_edge_downloader
```

This produces daily "nodes.csv" and "tweets.csv" files in the "daily_active_edge_friend_graphs_v5". Upload these CSV files to Google Drive, where we are running the impact assessment notebook w/ BERT classifier for each day. TODO: auto-upload to Google Drive.

## Oh also (v6)

Let's make a single large CSV file containing a row per user, and a list of their friends (who are also in our dataset):

```sql
CREATE TABLE impeachment_production.nodes_with_active_edges_v6 as (
  WITH au AS (
      SELECT
          cast(user_id as int64) as user_id
          ,upper(user_screen_name) as screen_name
          ,count(distinct status_id) as rate
      FROM impeachment_production.tweets t
      WHERE created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59' -- inclusive (primary collection period)
      GROUP BY 1,2
  )

  SELECT
      au.user_id
      ,au.screen_name
      ,au.rate
      ,CASE WHEN bu.community_id IS NOT NULL THEN TRUE ELSE FALSE END bot
      ,cast(bu.community_id as int64) as community_id
      ,STRING_AGG(DISTINCT uff.friend_name) as friend_names -- STRING AGG FOR CSV OUTPUT!
      ,count(DISTINCT uff.friend_name) as friend_count
  FROM au
  JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = au.user_id
  LEFT JOIN impeachment_production.2_bot_communities bu ON bu.user_id = au.user_id
  WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM au)
  GROUP BY 1,2,3,4,5
) -- THIS QUERY TAKES A LONG TIME :-D (3 min 13 sec) resulting in 2,869,590 rows
```

The table is too large to export to anywhere, so let's download it to CSV and manually upload to google drive:

```sh
#DESTRUCTIVE=true BATCH_SIZE=100 LIMIT=303 python -m app.bot_impact_v4.active_edge_v6_downloader

python -m app.bot_impact_v4.active_edge_v6_downloader
```


## JK (v7)

So the original assess data was made on bots in communities only, but we want all bots, regardless of their community assignment.

```sql
SELECT
  up.user_id
  ,up.screen_name
  ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
  ,bu.community_id

  ,bu.screen_names as bot_screen_names
  ,bu.screen_name_count as bot_screen_name_count


  ,up.follower_count
  ,up.status_count
  ,up.avg_score_lr
  ,up.avg_score_nb
  ,up.avg_score_bert
FROM impeachment_production.nlp_v2_predictions_by_user up
LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = up.user_id
-- WHERE bu.user_id IS NOT NULL and up.follower_count is not null
  -- and up.screen_name = "DRAGONS_ANGELS" -- up.user_id = 2838283974
WHERE up.user_id = 2838283974
ORDER BY bot_screen_name_count desc
LIMIT 10
```

```sql
SELECT
 p.user_id
 ,p.screen_name
 ,p.user_created_at
 -- ,p.status_id, status_text,
 ,p.score_lr, p.score_nb, p.score_bert
FROM impeachment_production.nlp_v2_predictions_combined p
-- LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = up.user_id
WHERE user_id = 2838283974
```

```sql

-- SN COUNT BOTS VS HUMANS

SELECT
  tp.user_id
  ,tp.user_created_at
  -- ,bu.screen_names
  -- ,bu.screen_name_count
  ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
  ,bu.community_id

  ,count(distinct tp.screen_name) as screen_name_count
  ,count(distinct tp.status_id) as status_count

  ,round(avg(tp.score_lr) * 10000) / 10000 as avg_score_lr -- round to four decimal places
  ,round(avg(tp.score_nb) * 10000) / 10000 as avg_score_nb -- round to four decimal places
  ,round(avg(tp.score_bert) * 10000) / 10000 as avg_score_bert -- round to four decimal places
FROM impeachment_production.nlp_v2_predictions_combined tp
LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = tp.user_id
WHERE tp.user_id = 2838283974
GROUP BY 1,2,3,4
```


```sql

CREATE TABLE impeachment_production.user_details_v4 AS (
  SELECT
    tp.user_id
    ,tp.user_created_at
    ,count(distinct tp.screen_name) as screen_name_count
    ,COALESCE(STRING_AGG(DISTINCT upper(tp.screen_name), ' | ') , "") as screen_names

    ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
    ,bu.community_id

    ,count(distinct tp.status_id) as status_count

    ,round(avg(tp.score_lr) * 10000) / 10000 as avg_score_lr -- round to four decimal places
    ,round(avg(tp.score_nb) * 10000) / 10000 as avg_score_nb -- round to four decimal places
    ,round(avg(tp.score_bert) * 10000) / 10000 as avg_score_bert -- round to four decimal places
  FROM impeachment_production.nlp_v2_predictions_combined tp
  LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = tp.user_id
  --WHERE tp.user_id = 2838283974
  GROUP BY 1,2,5,6
  -- LIMIT 100
)
```


OK here we go:


```sql
WITH scored_tweets as (
  SELECT
    tp.user_id ,tp.user_created_at ,tp.screen_name
    ,tp.status_id ,tp.created_at --,tp.status_text
    ,tp.score_lr ,tp.score_nb ,tp.score_bert
  FROM impeachment_production.nlp_v2_predictions_combined tp
  WHERE user_id = 2838283974
  --WHERE created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59' -- inclusive (primary collection period)
  --ORDER BY created_at
)

SELECT
  tp.user_id
  ,extract(date from tp.user_created_at) as user_created

  ,count(DISTINCT uff.friend_name) as user_friend_count
  --,STRING_AGG(DISTINCT uff.friend_name) as friend_names -- STRING AGG FOR CSV OUTPUT!

  ,tp.screen_name
  ,extract(date from min(tp.created_at)) as status_created_min
  ,extract(date from max(tp.created_at)) as status_created_max
  ,count(distinct tp.status_id) as status_count
  --,round(avg(tp.score_lr) * 10000) / 10000 as avg_score_lr -- round to four decimal places
  --,round(avg(tp.score_nb) * 10000) / 10000 as avg_score_nb -- round to four decimal places
  --,round(avg(tp.score_bert) * 10000) / 10000 as avg_score_bert -- round to four decimal places
   ,avg(tp.score_lr) as avg_score_lr -- round to four decimal places
  ,avg(tp.score_nb) as avg_score_nb -- round to four decimal places
  ,avg(tp.score_bert) as avg_score_bert

FROM scored_tweets as tp
LEFT JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = tp.user_id
--LEFT JOIN impeachment_production.user_friends_flat uff ON uff.screen_name = tp.screen_name

--WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM scored_tweets)
  --and tp.user_id = 2838283974
GROUP BY 1,2,4 --,4,5,6,7,8

```


```sql
-- ROW PER USER ID PER SCREEN NAME
CREATE TABLE impeachment_production.nodes_with_active_edges_v7_sn as (
  WITH scored_tweets as (
    SELECT
      tp.user_id ,tp.user_created_at ,tp.screen_name
      ,tp.status_id --,tp.created_at --,tp.status_text
      ,tp.score_lr ,tp.score_nb ,tp.score_bert
    FROM impeachment_production.nlp_v2_predictions_combined tp
    --WHERE user_id = 2838283974
    WHERE created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59' -- inclusive (primary collection period)
    --ORDER BY created_at
  )

  SELECT
    tp.user_id
    ,extract(date from tp.user_created_at) as user_created

    ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
    ,bu.community_id

    ,count(DISTINCT uff.friend_name) as active_friend_count
    ,STRING_AGG(DISTINCT uff.friend_name) as active_friend_names -- STRING AGG FOR CSV OUTPUT!

    ,tp.screen_name
    --,extract(date from min(tp.created_at)) as status_created_min
    --,extract(date from max(tp.created_at)) as status_created_max
    ,count(distinct tp.status_id) as status_count
    ,avg(tp.score_lr) as avg_score_lr -- round to four decimal places
    ,avg(tp.score_nb) as avg_score_nb -- round to four decimal places
    ,avg(tp.score_bert) as avg_score_bert

  FROM scored_tweets as tp
  LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = tp.user_id
  LEFT JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = tp.user_id
  WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM scored_tweets)
  GROUP BY user_id, user_created, is_bot, community_id, screen_name
) -- TAKES A FEW MINUTES
```

```sql
-- ROW PER USER ID
CREATE TABLE impeachment_production.nodes_with_active_edges_v7_id as (
  WITH scored_tweets as (
    SELECT
      tp.user_id ,tp.user_created_at ,tp.screen_name
      ,tp.status_id ,tp.created_at --,tp.status_text
      ,tp.score_lr ,tp.score_nb ,tp.score_bert
    FROM impeachment_production.nlp_v2_predictions_combined tp
    --WHERE user_id = 2838283974
    WHERE created_at BETWEEN '2019-12-20 00:00:00' AND '2020-02-15 23:59:59' -- inclusive (primary collection period)
    --ORDER BY created_at
  )

  SELECT
    tp.user_id
    ,extract(date from tp.user_created_at) as user_created

    ,CASE WHEN bu.user_id IS NOT NULL THEN true ELSE false END is_bot
    ,bu.community_id

    ,count(DISTINCT uff.friend_name) as friend_count
    ,STRING_AGG(DISTINCT uff.friend_name) as friend_names -- STRING AGG FOR CSV OUTPUT!

    --,tp.screen_name
    --,count(distinct tp.screen_name) as screen_name_count
    --,STRING_AGG(DISTINCT tp.screen_name) as screen_names -- STRING AGG FOR CSV OUTPUT!
    --,extract(date from min(tp.created_at)) as status_created_min
    --,extract(date from max(tp.created_at)) as status_created_max
    ,count(distinct tp.status_id) as status_count

    ,round(avg(tp.score_lr) * 10000) / 10000 as avg_score_lr -- round to four decimal places
    ,round(avg(tp.score_nb) * 10000) / 10000 as avg_score_nb -- round to four decimal places
    ,round(avg(tp.score_bert) * 10000) / 10000 as avg_score_bert -- round to four decimal places

  FROM scored_tweets as tp
  LEFT JOIN impeachment_production.bots_above_80_v2 bu ON bu.user_id = tp.user_id
  LEFT JOIN impeachment_production.user_friends_flat uff ON cast(uff.user_id as int64) = tp.user_id
  WHERE uff.friend_name in (SELECT DISTINCT screen_name FROM scored_tweets)
  GROUP BY user_id, user_created, is_bot, community_id --, screen_name
) -- TAKES A FEW MINUTES
```

```sql
/*
SELECT
-- count(distinct user_id)  -- 2,869,590 --, sum(status_count)  -- 50,372,443
  user_id ,count(distinct screen_name) as sn_count
FROM impeachment_production.nodes_with_active_edges_v7_sn
GROUP BY 1
HAVING sn_count > 3 and sn_count < 10
LIMIT 100

*/

SELECT
  user_id, user_created, is_bot, community_id
  ,friend_count -- ,friend_names
  --,screen_name_count  --,screen_names
  ,status_count
  ,avg_score_lr
  ,avg_score_nb
  ,avg_score_bert

FROM impeachment_production.nodes_with_active_edges_v7_id
--WHERE user_id = 2838283974
--WHERE user_id = 1207729717635436545
WHERE user_id = 1136942510771724289

```










The table is too large to export to anywhere, so let's download it to CSV and manually upload to google drive:

```sh
#DESTRUCTIVE=true BATCH_SIZE=100 LIMIT=303 python -m app.bot_impact_v4.active_edge_v7_downloader

python -m app.bot_impact_v4.active_edge_v7_downloader
```
