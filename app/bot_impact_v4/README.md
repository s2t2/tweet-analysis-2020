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
