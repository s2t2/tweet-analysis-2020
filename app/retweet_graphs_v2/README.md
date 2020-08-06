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

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2
.lookup_user_ids # will probably hit rate limits, but will auto-sleep and restart when able

```


Analyzing the results...

```sql
/*
select
  count(screen_name) -- 17196
  ,count(distinct screen_name) -- 17193

  ,count(user_id) -- 14971
  ,count(distinct user_id) -- 14969
from impeachment_production.user_id_lookups idl
*/


/*
select
  screen_name
  ,count(distinct user_id) as id_count
from impeachment_production.user_id_lookups idl
group by 1
having id_count > 1
-- no results GOOD
 */

select
  user_id
  ,count(distinct upper(screen_name)) as sn_count
from impeachment_production.user_id_lookups idl
group by 1
having sn_count > 1
-- null user id for 2224 screen names, but no others. would expect some to show up here

```







```sql

-- TODO: need to make a master table of users
-- TODO: make a screen name lookup table where you can get the corresponding user id of the screen name
(

    -- this isn't right. need to have uniqueness
    SELECT
        user_id
        ,upper(user_screen_name) as screen_name
    FROM impeachment_production.tweets
    --ORDER BY user_id

)
UNION ALL
(
  select
    /*case
      when user_id is null then concat('DEACTIVE-', upper(screen_name))
      else user_id
      end user_id
      */
      user_id
      ,upper(screen_name) as screen_name
  from impeachment_production.user_id_lookups
  where user_id is not null -- 14,971
  -- order by user_id
)

```

Of 17K users, 15K have user ids. What about the others?


```sql
/*select *
from impeachment_production.retweets rt
limit 10
*/

DROP TABLE IF EXISTS impeachment_production.idless_users;
CREATE TABLE impeachment_production.idless_users as (
  select
    idl.screen_name
    ,case when idl.message = 'User not found.' then 'NOT-FOUND'
      when idl.message = 'User has been suspended.' then 'SUSPENDED'
      end lookup_error
  from impeachment_production.user_id_lookups idl
  where idl.user_id is null and idl.message is not null
  order by 1
)

```


```sql
SELECT
  i.screen_name --- the retweeter
  ,i.lookup_error
  ,count(distinct rt.status_id) as retweet_count
  ,count(distinct rt.user_id) as retweeter_count
FROM impeachment_production.idless_users i
LEFT JOIN impeachment_production.retweets rt ON upper(rt.user_screen_name) = upper(i.screen_name)
GROUP BY 1,2
ORDER by 3 desc
-- only two users without ids have done any retweeting, and their tweet total is 2
```

```sql
SELECT
  i.screen_name -- the retweeted
  ,i.lookup_error
  ,count(distinct rt.status_id) as retweet_count
  ,count(distinct rt.user_id) as retweeter_count
FROM impeachment_production.idless_users i
LEFT JOIN impeachment_production.retweets rt ON upper(rt.retweet_user_screen_name) = upper(i.screen_name)
GROUP BY 1,2
ORDER by 3 desc
-- 2224 users without ids have been retweeted, some thousands of times. interesting. exporting to sheets.


```


```sql
-- it could be that these screen names are old and we have a match?

SELECT
  i.screen_name
  ,i.lookup_error
  ,count(distinct d.user_id) as user_id_count
FROM impeachment_production.idless_users i
JOIN impeachment_production.user_details d ON upper(i.screen_name) in UNNEST(d.screen_names)
GROUP BY 1,2
ORDER by 3 desc

-- only two users match.
```








## Retweet Graphs

Loading existing graphs based on
```sh
LOCAL_DIRPATH="data/graphs/weekly/2020-12" python -m app.retweet_graphs_v2.storage
```
