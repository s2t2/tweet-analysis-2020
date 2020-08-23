
# PG Pipeline

## Installing PostgreSQL

```sh
brew install postgresql
brew services start postgresql
createdb
```

```sh
# inside the virtual environment:
pip install psycopg2
```

## Creating Local Database

```sql
CREATE DATABASE impeachment_analysis;
```

## Local Database Migration

Testing the local PostgreSQL database connection:

```sh
python -m app.pg_pipeline.models
```

Downloading the "tweets" table (if it isn't too big):

```sh
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 python -m app.pg_pipeline.tweets
```

Downloading the "user_friends" table:

```sh
#python -m app.pg_pipeline.user_friends
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=1000 python -m app.pg_pipeline.user_friends
```

Downloading the "user_details" table:

```sh
#BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true USERS_LIMIT=1000 BATCH_SIZE=300 python -m app.pg_pipeline.user_details
BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true BATCH_SIZE=2500 python -m app.pg_pipeline.user_details
```

Downloading the "retweeter_details" table:

```sh

# BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true USERS_LIMIT=1000 BATCH_SIZE=300 python -m app.pg_pipeline.retweeter_details
BIGQUERY_DATASET_NAME="impeachment_production" PG_DESTRUCTIVE=true BATCH_SIZE=2500 python -m app.pg_pipeline.retweeter_details
```


<hr>





# User Analysis Notes

## User Details

```sql
DROP TABLE IF EXISTS impeachment_production.user_details;
CREATE TABLE impeachment_production.user_details as (
  SELECT
    user_id

    ,count(DISTINCT upper(user_screen_name)) as _screen_name_count
    ,ARRAY_AGG(DISTINCT upper(user_screen_name) IGNORE NULLS) as _screen_names
    ,ANY_VALUE(user_screen_name) as screen_name

    ,count(DISTINCT upper(user_name)) as _name_count
    ,ARRAY_AGG(DISTINCT upper(user_name) IGNORE NULLS) as _names
    ,ANY_VALUE(user_name) as name

    ,count(DISTINCT upper(user_description)) as _description_count
    ,ARRAY_AGG(DISTINCT upper(user_description) IGNORE NULLS) as _descriptions
    ,ANY_VALUE(user_description) as description

    ,count(DISTINCT upper(user_location))	 as _location_count
    ,ARRAY_AGG(DISTINCT upper(user_location) IGNORE NULLS) as _locations
    ,ANY_VALUE(user_location) as location

    ,count(DISTINCT user_verified)	as _verified_count #>  1
    ,ARRAY_AGG(DISTINCT user_verified IGNORE NULLS) as _verifieds
    ,ANY_VALUE(user_verified) as verified

    ,count(DISTINCT user_created_at) _created_at_count #>  1
    ,ARRAY_AGG(DISTINCT user_created_at IGNORE NULLS) as _created_ats
    ,ANY_VALUE(user_created_at) as created_at

  FROM impeachment_production.tweets
  GROUP BY user_id
);
```


Get max character lengths for defining the user details table in PG:

```sql
select
  max(CHAR_LENGTH(user_screen_name)) -- 18
  ,max(CHAR_LENGTH(user_name)) -- 50
  ,max(CHAR_LENGTH(user_description)) -- 244
  ,max(CHAR_LENGTH(user_location)) -- 150
from impeachment_production.tweets
```



Local queries to setup a Tableau workbook:

```sql
SELECT
  d.user_id
FROM user_details d
LEFT JOIN user_friends f ON d.user_id = f.user_id
WHERE f.friend_count is null
-- 16 rows don't have a friends count:
-- [230445365,884098078025826306,2950024043,765688750433308673,1216006276171423745,289782531,840065711590453251,507389727,1537305158,857227225116135424,16517574,792427950,1117910067846766597,2909713302,2847944058,2901662253]
```


For tableau workbooks, let's start with building and contrasting two example communities, to build and demonstrate analysis capabilities before we come back with an updated bot classification methodology.

For an example community to represent non-bots, let's use the 28,000 twitter-verified users:

```sql
select count(distinct user_id) as user_count
from user_details
where verified = true -- 28297
```

For an example community to represent bots, let's use the 31,000 who have used more than one screen name during the collection period:

```sql
select count(distinct user_id) as user_count
from user_details
where screen_name_count > 1 -- 31165
```


And maybe we'll also throw in a group of users in neither category, with a decent amount of people they follow:

```sql
select count(distinct d.user_id) as user_count
from user_details d
JOIN user_friends f ON d.user_id = f.user_id
where
  -- f.friend_count >= 2000 -- 339,775
  -- f.friend_count BETWEEN 1800 and 1900 -- 22720
  f.friend_count BETWEEN 1750 and 1900 -- 34,805
```

Assigning the users to communities:

```sql
SELECT
  d.user_id, d.screen_name, d.name, d.description, d.location, d.verified, d.created_at

  ,f.friend_count

  ,d.screen_name_count, d.name_count, d.description_count, d.location_count, d.verified_count, d.created_count

  ,CASE
      -- for 24 who are both verified and >1 screen name, assign to verified category
      WHEN d.verified = true THEN 'VERIFIED'
      WHEN d.screen_name_count > 1 THEN 'SCREEN_NAME_UPDATER'
      WHEN f.friend_count BETWEEN 1750 and 1900 THEN 'MANY_FRIENDS'
    END community_assignment

  ,d.screen_names, d.names, d.descriptions, d.locations

FROM user_details d
JOIN user_friends f ON d.user_id = f.user_id
WHERE screen_name_count > 1 -- 31165
      or verified = true -- 28297
      or f.friend_count BETWEEN 1750 and 1900
```


Exporting this exploratory dataset of 128,410 users as "expore_users.csv". Importing data into Tableau...

![](/workbooks/explore_users/users_created.png)

Let's do a more comprehensive job of clustering users into communities, first using conversation topic-specific communities. Adding topic counts to the "user_details" query, re-creating the table, re-downloading it to local PG. Importing into Tableau...

```sql
DROP TABLE IF EXISTS `impeachment_production.user_details`;
CREATE TABLE `impeachment_production.user_details` as (
    SELECT
        t.user_id

        -- USER DETAILS

        ,count(DISTINCT upper(t.user_screen_name)) as screen_name_count
        ,count(DISTINCT upper(t.user_name)) as name_count
        ,count(DISTINCT upper(t.user_description)) as description_count
        ,count(DISTINCT upper(t.user_location))	 as location_count
        ,count(DISTINCT t.user_verified)	as verified_count
        ,count(DISTINCT t.user_created_at) created_at_count

        ,ARRAY_AGG(DISTINCT upper(t.user_screen_name) IGNORE NULLS) as screen_names
        ,ARRAY_AGG(DISTINCT upper(t.user_name) IGNORE NULLS) as names
        ,ARRAY_AGG(DISTINCT upper(t.user_description) IGNORE NULLS) as descriptions
        ,ARRAY_AGG(DISTINCT upper(t.user_location) IGNORE NULLS) as locations
        ,ARRAY_AGG(DISTINCT t.user_verified IGNORE NULLS) as verifieds
        ,ARRAY_AGG(DISTINCT t.user_created_at IGNORE NULLS) as created_ats

        ,ANY_VALUE(t.user_screen_name) as screen_name
        ,ANY_VALUE(t.user_name) as name
        ,ANY_VALUE(t.user_description) as description
        ,ANY_VALUE(t.user_location) as location
        ,ANY_VALUE(t.user_verified) as verified
        ,ANY_VALUE(t.user_created_at) as created_at

        -- TWEET / CONVERSATION TOPIC DETAILS

        ,count(distinct t.status_id) as status_count
        ,count(distinct t.retweet_status_id) as retweet_count
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#IMPEACHANDCONVICT') then status_id end) as impeach_and_convict
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#SENATEHEARING') then status_id end) as senate_hearing
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#IGHEARING') then status_id end) as ig_hearing
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#FACTSMATTER') then status_id end) as facts_matter
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#SHAMTRIAL') then status_id end) as sham_trial
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#MAGA') then status_id end) as maga
        ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), '#ACQUITTEDFOREVER') then status_id end) as acquitted_forever

        -- FRIEND / FOLLOWER DETAILS

        ,max(f.friend_count) as friend_count

    FROM `impeachment_production.tweets` t
    JOIN `impeachment_production.user_friends` f ON t.user_id = f.user_id
    GROUP BY t.user_id
);
```

```sql
 -- select user_id, screen_name, status_count, retweet_count, screen_name_count, created_at, created_count from user_details where created_at < '2000-01-01' -- 5 users created at '1969-12-31 19:00:00' who account for 8 tweets (7 of them retweets)


-- select * from user_details where created_count > 1  -- no rows

-- select * from user_details where verified_count > 1 -- no rows

 select
   user_id
   ,location
   ,verified
   ,created_at
   ,screen_name_count ,name_count ,description_count ,location_count --, verified_count, created_count
   ,friend_count
   ,status_count as tweet_count
   ,retweet_count
   ,impeach_and_convict ,senate_hearing ,ig_hearing ,facts_matter ,sham_trial ,maga ,acquitted_forever
 from user_details where created_at > '1970-01-01' -- filter out 5 rows with weird creation on new years 1969-12-31 19:00:00'
```

![](/workbooks/user_details/users_created.png)
![](/workbooks/user_details/users_created_verified.png)
![](/workbooks/user_details/users_created_screen_name_changers.png)
![](/workbooks/user_details/users_created_retweeters.png)

By topic:

![](/workbooks/user_details/users_created_topic_impeach_and_convict.png)
![](/workbooks/user_details/users_created_topic_maga.png)
![](/workbooks/user_details/users_created_topic_sham_trial.png)


## Retweeter Details

```sql
DROP TABLE IF EXISTS impeachment_production.retweeter_details;
CREATE TABLE IF NOT EXISTS impeachment_production.retweeter_details as (
  SELECT
    subq.*
    --,d.screen_name
    --,d.name
    --,d.description
    -- ,d.location
    ,d.created_at
    ,d.screen_name_count
    ,d.name_count
    ,d.verified
  FROM (
    SELECT
      rt.user_id
      -- ,any_value(user_screen_name) as screen_name
      --,status_text
      -- ,created_at
      --,retweet_user_screen_name
      ,count(distinct rt.status_id) as retweet_count
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#IGREPORT') then rt.status_id end) as ig_report
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#IGHEARING') then rt.status_id end) as ig_hearing
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#SENATEHEARING') then rt.status_id end) as senate_hearing
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#NOTABOVETHELAW') then rt.status_id end) as not_above_the_law
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#IMPEACHANDCONVICT') then rt.status_id end) as impeach_and_convict
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#IMPEACHANDREMOVE') then rt.status_id end) as impeach_and_remove
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#FACTSMATTER') then rt.status_id end) as facts_matter
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#SHAMTRIAL') then rt.status_id end) as sham_trial
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#MAGA') then rt.status_id end) as maga
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#ACQUITTEDFOREVER') then rt.status_id end) as acquitted_forever
      ,count(distinct case when REGEXP_CONTAINS(upper(rt.status_text), '#COUNTRY_OVER_PARTY') then rt.status_id end) as country_over_party
    FROM impeachment_production.retweets rt
    WHERE rt.user_screen_name <> rt.retweet_user_screen_name -- exclude people retweeting themselves!
    GROUP BY rt.user_id
    -- ORDER BY retweet_count desc
  ) subq
  JOIN impeachment_production.user_details d ON d.user_id = subq.user_id
)
```

![](/workbooks/retweeter_details/users_created.png)

![](/workbooks/retweeter_details/users_created_screen_name_changers.png)

![](/workbooks/retweeter_details/users_created_name_changers.png)

By topic:

![](/workbooks/retweeter_details/users_created_topic_acquitted_forever.png)
![](/workbooks/retweeter_details/users_created_topic_facts_matter.png)
![](/workbooks/retweeter_details/users_created_topic_ig_hearing.png)
![](/workbooks/retweeter_details/users_created_topic_ig_report.png)
![](/workbooks/retweeter_details/users_created_topic_impeach_and_convict.png)
![](/workbooks/retweeter_details/users_created_topic_impeach_and_remove.png)
![](/workbooks/retweeter_details/users_created_topic_maga.png)
![](/workbooks/retweeter_details/users_created_topic_not_above_the_law.png)
![](/workbooks/retweeter_details/users_created_topic_senate_hearing.png)
![](/workbooks/retweeter_details/users_created_topic_sham_trial.png)

## Retweet Beneficiaries

Right-leaning topic beneficiaries:

```sql
SELECT
  retweet_user_screen_name
  ,count(distinct status_id) as retweet_count
  ,count(distinct user_id) as retweeter_count
FROM impeachment_production.retweets rt
WHERE REGEXP_CONTAINS(upper(rt.status_text), '#MAGA')
   OR REGEXP_CONTAINS(upper(rt.status_text), '#SHAMTRIAL')
   OR REGEXP_CONTAINS(upper(rt.status_text), '#ACQUITTEDFOREVER')
   -- () AND user_screen_name <> retweet_user_screen_name
GROUP BY retweet_user_screen_name
ORDER BY retweet_count DESC
LIMIT 100
```

Left-leaning topic beneficiaries:


```sql
SELECT
  retweet_user_screen_name
  ,count(distinct status_id) as retweet_count
  ,count(distinct user_id) as retweeter_count
FROM impeachment_production.retweets rt
WHERE REGEXP_CONTAINS(upper(rt.status_text), '#IMPEACHANDREMOVE')
   OR REGEXP_CONTAINS(upper(rt.status_text), '#IMPEACHANDCONVICT')
   OR REGEXP_CONTAINS(upper(rt.status_text), '#NOTABOVETHELAW')
   -- () AND user_screen_name <> retweet_user_screen_name
GROUP BY retweet_user_screen_name
ORDER BY retweet_count DESC
LIMIT 100
```


## Retweets


```sql
select
  t.*
  ,rt.retweet_user_screen_name
from impeachment_production.retweets rt
JOIN impeachment_production.tweets t ON rt.status_id = t.status_id
where REGEXP_CONTAINS(upper(rt.status_text), '#TRUMPLETTER')
order by t.created_at
```

## Retweeter Creation Dates


```sql
/*
select
   count(distinct CASE WHEN d.maga >= 1 THEN user_id END) x_count -- 34,236
   ,count(distinct CASE WHEN d.impeach_and_remove >= 1 THEN user_id END) y_count -- 22,768
from retweeter_details d
*/

/*
select
   count(distinct CASE WHEN d.maga > 0 and d.impeach_and_remove > 0 THEN user_id END) both_count
   ,count(distinct CASE WHEN d.maga = 0 and d.impeach_and_remove = 0 THEN user_id END) neither_count
      ,count(distinct CASE WHEN d.maga > 0 and d.impeach_and_remove = 0 THEN user_id END) x_count
   ,count(distinct CASE WHEN d.maga = 0 AND d.impeach_and_remove > 0 THEN user_id END) y_count
from retweeter_details d
-- 4476	2702472	29760	18292
*/

/*
select
   count(distinct CASE WHEN d.sham_trial > 0 and d.not_above_the_law > 0 THEN user_id END) both_count
   ,count(distinct CASE WHEN d.sham_trial = 0 and d.not_above_the_law = 0 THEN user_id END) neither_count
   ,count(distinct CASE WHEN d.sham_trial > 0 and d.not_above_the_law = 0 THEN user_id END) x_count
   ,count(distinct CASE WHEN d.sham_trial = 0 AND d.not_above_the_law > 0 THEN user_id END) y_count
from retweeter_details d
-- 1145	2737845	10245	5765
*/

/*
select
   count(distinct CASE WHEN d.sham_trial > 0 and d.country_over_party > 0 THEN user_id END) both_count
   ,count(distinct CASE WHEN d.sham_trial = 0 and d.country_over_party = 0 THEN user_id END) neither_count
   ,count(distinct CASE WHEN d.sham_trial > 0 and d.country_over_party = 0 THEN user_id END) x_count
   ,count(distinct CASE WHEN d.sham_trial = 0 AND d.country_over_party > 0 THEN user_id END) y_count
from retweeter_details d
--  0	2743610	11390	0
*/

select
   count(distinct CASE WHEN d.acquitted_forever > 0 and d.not_above_the_law > 0 THEN user_id END) both_count
   ,count(distinct CASE WHEN d.acquitted_forever = 0 and d.not_above_the_law = 0 THEN user_id END) neither_count
   ,count(distinct CASE WHEN d.acquitted_forever > 0 and d.not_above_the_law = 0 THEN user_id END) x_count
   ,count(distinct CASE WHEN d.acquitted_forever = 0 AND d.not_above_the_law > 0 THEN user_id END) y_count
from retweeter_details d
--  17	2744356	3734	6893
```



## Bot Classifications

After generating bot classifications, import the results into BigQuery and the local PG database as a table named "bot_probabilities".

Run this query against local PG and export the results as "user_details_with_bot_probabilities.csv" then load the results into Tableau.

```sql
select
  ud.user_id
  ,ud.screen_name
  ,ud.verified
  ,ud.created_at
  ,ud.screen_name_count
  ,ud.name_count
  ,ud.description_count
  ,ud.location_count
  ,ud.friend_count
  ,ud.status_count
  ,ud.retweet_count

  ,b.bot_probability
  -- ,case when b.bot_probability > .5
from bot_probabilities b
join user_details ud on ud.screen_name = b.screen_name

```


Run this queries against BigQuery to get retweet beneficiaries, then save the result to CSV and upload to Google Sheets for sharing:


```sql
select
  *
  -- ,bot_retweet_count / human_retweet_count as bot_to_human_retweet_ratio
  -- ,bot_retweeter_count / human_retweeter_count as bot_to_human_retweeter_ratio
  ,SAFE_DIVIDE(bot_retweet_count, human_retweet_count) as bot_to_human_retweet_ratio
  ,SAFE_DIVIDE(bot_retweeter_count, human_retweeter_count) as bot_to_human_retweeter_ratio

FROM (

  SELECT
    retweet_user_screen_name
    ,count(distinct status_id) as retweet_count
    ,count(distinct user_id) as retweeter_count

    ,count(distinct CASE WHEN b.bot_probability < .9 THEN status_id END) as human_retweet_count
    ,count(distinct CASE WHEN b.bot_probability < .9 THEN user_id END) as human_retweeter_count

    ,count(distinct CASE WHEN b.bot_probability >= .9 THEN status_id END) as bot_retweet_count
    ,count(distinct CASE WHEN b.bot_probability >= .9 THEN user_id END) as bot_retweeter_count


  FROM impeachment_production.retweets rt
  LEFT JOIN impeachment_production.bot_probabilities b on b.screen_name = rt.user_screen_name
  GROUP BY retweet_user_screen_name
  -- ORDER BY retweet_count DESC
) subq

ORDER BY retweet_count DESC
LIMIT 10000 -- big query export maximum 16000 rows to local CSV
```
