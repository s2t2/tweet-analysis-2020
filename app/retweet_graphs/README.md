
# Retweet Graphs

Constructing retweet graphs:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 TOPIC="impeach" python -m app.retweet_graphs.bq_retweet_grapher

BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 TOPIC="#MAGA" python -m app.retweet_graphs.bq_retweet_grapher

BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 "#ImpeachAndConvict" python -m app.retweet_graphs.bq_retweet_grapher
```

Observe the resulting job identifier (`JOB_ID`), and verify the graph and other artifacts are saved to local storage and/or Google Cloud Storage.

Once you have created a retweet graph, note its `JOB_ID`, and see how much memory it takes to load a given graph:

```sh
# right-leaning conversation graph
JOB_ID="2020-06-07-2049" STORAGE_MODE="local" python -m app.friend_graphs.graph_analyzer
JOB_ID="2020-06-07-2049" STORAGE_MODE="remote" python -m app.friend_graphs.graph_analyzer

# left-leaning conversation graph
JOB_ID="2020-06-07-2056" STORAGE_MODE="local" python -m app.friend_graphs.graph_analyzer
JOB_ID="2020-06-07-2056" STORAGE_MODE="remote" python -m app.friend_graphs.graph_analyzer

# neutral conversation retweet graph
JOB_ID="2020-06-15-2141" STORAGE_MODE="local" python -m app.friend_graphs.graph_analyzer
```

## Weekly Retweet Graphs

Constructing retweet graphs for a given week in the dataset:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=2500 python -m app.retweet_graphs.bq_weekly_grapher
# BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=2500 WEEK_ID="2019-52" python -m app.retweet_graphs.bq_weekly_grapher
```

Load weekly retweet graphs to see how much memory it takes:

```sh
WEEK_ID="2019-52" python -m app.retweet_graphs.bq_weekly_graph_loader
```

## Bot Classification

Once you have created a retweet graph, note its `JOB_ID` or `WEEK_ID`, then compute bot probabilities for each node:

```sh
# JOB_ID="2020-06-15-2141" python -m app.botcode_v2.classifier
JOB_ID="2020-06-15-2141" DRY_RUN="false" python -m app.botcode_v2.classifier
```

```sh
# WEEK_ID="2019-52" python -m app.retweet_graphs.bq_weekly_graph_bot_classifier
WEEK_ID="2019-52" DRY_RUN="false" python -m app.retweet_graphs.bq_weekly_graph_bot_classifier
```

## KS Tests

### Retweeter Age Distribution By Topic

Compare the distribution of user creation dates for those retweeting about a given topic, vs those not retweeting about that topic:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" TOPIC="#ImpeachAndConvict" python -m app.ks_test.topic_analyzer
```

### Retweeter Age Distribution By Topic Pair

Compare the distribution of user creation dates for those retweeting exclusively about one of two different topics:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" X_TOPIC="#ImpeachAndConvict" Y_TOPIC="#MAGA" python -m app.ks_test.topic_pair_analyzer
```














<hr>





# Retweet Graph Notes

Migrate and populate a few tables which we'll use to construct mention graphs.

First, for each tweet that is a retweet, determine the screen names of the user (i.e. retweeter) and the retweet user (i.e. retweeted) in a new table called "retweets":

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
SELECT count(DISTINCT status_id)
FROM impeachment_production.retweets;
```

Of the 67M tweets, 55.9M are retweets.

Let's count how many times each user retweeted another, in a new table called "retweet_counts":

```sql
DROP TABLE IF EXISTS impeachment_production.retweet_counts;
CREATE TABLE IF NOT EXISTS impeachment_production.retweet_counts as (
  SELECT
    user_id
    ,user_screen_name
    ,retweet_user_screen_name
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.retweets
  GROUP BY 1,2,3
);
```

For the 55M retweets, there are 2.7M users who did the retweeting. This is compared to the 3.6M users total.

```sql
SELECT count(DISTINCT user_id)
FROM impeachment_production.retweet_counts;
```

It seems there are many users who retweeted themselves hundreds or thousands of times. Perhaps we want to filter them out of a table that will construct the rt graphs. Although it is possible they could indicate bot behavior.

```sql
SELECT user_id, user_screen_name, retweet_user_screen_name, retweet_count
FROM impeachment_production.retweet_counts
order by retweet_count desc
limit 100
```

Which users were retweeted the most?

```sql
select retweet_user_screen_name, count(distinct user_id) as rt_by_users_count, count(distinct status_id) as rt_count
from impeachment_production.retweets
group by 1
order by 2 desc
limit 25
```


retweet_user_screen_name | rt_by_users_count | rt_count
--- | --- | ---
realDonaldTrump | 330211 | 2572421
charliekirk11 | 261486 | 1235210
SethAbramson | 137606 | 536125
gtconway3d | 133292 | 536097
tribelaw | 121937 | 639320
RepAdamSchiff | 117465 | 293892
SpeakerPelosi | 114274 | 226393
funder | 112302 | 394151
dbongino | 110514 | 456759
DonaldJTrumpJr | 104977 | 334537
JoyceWhiteVance | 102185 | 472908
kylegriffin1 | 98250 | 389961
RepMarkMeadows | 98027 | 434223
RudyGiuliani | 89722 | 266291
marklevinshow | 87526 | 331255
GOPLeader | 87211 | 276222
mmpadellan | 80404 | 200454
RealJamesWoods | 79354 | 157840
joncoopertweets | 79340 | 212499
justinamash | 79183 | 166078
w_terrence | 78612 | 185069
TomFitton | 78148 | 405667
RyanAFournier | 78090 | 179753
TheRickWilson | 77116 | 172818
senatemajldr | 75212 | 191118


Identify which users were retweeted the most, about a given topic:

```sql
SELECT
  retweet_user_screen_name
  ,count(distinct user_id) as retweet_user_count
  ,sum(retweet_count) as retweeted_total
FROM (
  SELECT
    rt.user_id
    ,rt.user_screen_name
    ,rt.retweet_user_screen_name
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.retweets rt
  WHERE upper(rt.status_text) LIKE '%#IMPEACHANDCONVICT%' -- AND (created_at BETWEEN  AND '{end_at}')
    AND rt.user_screen_name <> rt.retweet_user_screen_name -- exlude people retweeting themselves, right?
  GROUP BY 1,2,3
  -- ORDER BY 4 desc
)
GROUP BY retweet_user_screen_name
ORDER BY 3 DESC
```

Constructing Retweet Graphs:

```json
{
  "app_env": "development",
  "job_id": "2020-06-15-2141",
  "dry_run": false,
  "batch_size": 1000,
  "dataset_address": "tweet-collector-py.impeachment_production",
  "destructive": false,
  "verbose": false,
  "retweeters": true,
  "conversation":

  {"users_limit": 50000, "topic": "impeach", "start_at": "2020-01-01", "end_at": "2020-01-30"}
}
```

# Updated Migrations

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

Begin to reverse-engineer retweeted user ids:

```sql
drop table if exists impeachment_development.retweeted_users;
create table impeachment_development.retweeted_users as (
  select
      retweet_user_screen_name,
      count(distinct status_id) as retweeted_count
  from impeachment_development.retweets
  group by 1
  order by 2 desc
)
```
