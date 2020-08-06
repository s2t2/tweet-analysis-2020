# Retweet Graphs v2

## BigQuery Migrations

We need to make graphs using user ids, not screen names. Because screen names can change. So let's construct some tables on BigQuery for user screen name to id conversion.

```sql
DROP TABLE IF EXISTS impeachment_production.retweets;
CREATE TABLE IF NOT EXISTS impeachment_production.retweets as (
  SELECT
    user_id
    ,user_created_at
    ,user_screen_name
    ,split(SPLIT(status_text, "@")[OFFSET(1)], ":")[OFFSET(0)] as retweet_user_screen_name
    ,status_id
    ,status_text
    ,created_at
  FROM impeachment_production.tweets
  WHERE retweet_status_id is not null
);
```

```sql
--DROP TABLE IF EXISTS impeachment_production.user_screen_names;
--CREATE TABLE impeachment_production.user_screen_names as (
  SELECT DISTINCT screen_name
  FROM (
    SELECT DISTINCT user_screen_name as screen_name FROM impeachment_production.tweets
    UNION ALL
    SELECT DISTINCT retweet_user_screen_name as screen_name FROM impeachment_production.retweets
  ) subq
  ORDER BY screen_name
--);


-- from tweets, there can be many screen names per user id
-- first lets get all the unique screen names of those tweeting and being retweeted
-- we can use the retweets table which has the retweeted user screen name, but we'll have to assign them unique ids or fetch their ids from twitter. will we be able to find them all? next time get them immediately after collecting the tweet.
-- but the bots are the ones doing the retweeting, so we have their ids, so things should be fine if we assign unique ids for each retweeted user screen name, or use the screen name itself.
-- so we need a column with screen name as the primary key
-- and another column of the corresponding user id (as a string is fine)
```


```sql
SELECT
  count(distinct sn.screen_name) as sn_count -- 3,653,231
  ,count(distinct CASE WHEN t.user_id IS NULL THEN sn.screen_name END) as idless_sn_count -- 17,196
  ,count(distinct t.user_id) as id_count -- 3,600,545
FROM impeachment_production.user_screen_names sn
LEFT JOIN impeachment_production.tweets t on t.user_screen_name = sn.screen_name
```

Only fetching ids for 17K users...

```sh
python app.retweet_graphs_v2.lookup_user_ids
```
