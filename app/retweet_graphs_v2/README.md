# Retweet Graphs v2

## Prep

### BigQuery Migrations

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

### User Id Lookups

The first verion of the tweet collector didn't include user ids for retweeted users, so we're looking them up:

```sh
# python -m app.retweet_graphs_v2.prep.lookup_user_ids

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.lookup_user_ids
```

### User Id Assignments

Some (2,224) of the users looked up were "not found" or "suspended", so we're assigning unique identifiers for those users (just to use during retweet graph compilation):

```sh
# python -m app.retweet_graphs_v2.prep.assign_user_ids

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.assign_user_ids
```

### More BigQuery Migrations

User screen names table (one id has many screen names):

```sh
# python -m app.retweet_graphs_v2.prep.migrate_user_screen_names

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.migrate_user_screen_names
```

New user details table (row per user id):

```sh
# python -m app.retweet_graphs_v2.prep.migrate_user_details_v2

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.migrate_user_details_v2
```

New retweets table (includes retweeted user id):

```sh
# python -m app.retweet_graphs_v2.prep.migrate_retweets_v2

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.migrate_retweets_v2
```

Empty table which will store bot classifications:

```sh
# python -m app.retweet_graphs_v2.prep.migrate_daily_bot_probabilities

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.prep.migrate_daily_bot_probabilities

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_test" python -m app.retweet_graphs_v2.prep.migrate_daily_bot_probabilities
```



## Retweet Graphs

Storing and loading a mock graph:

```sh
python -m app.retweet_graphs_v2.graph_storage
# DIRPATH="path/to/existing/dir" python -m app.retweet_graphs_v2.graph_storage
```

Constructing and storing example graphs:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" DRY_RUN="true" python -m app.retweet_graphs_v2.retweet_grapher

BIGQUERY_DATASET_NAME="impeachment_production" DIRPATH="graphs/example" USERS_LIMIT=1000 BATCH_SIZE=100 python -m app.retweet_graphs_v2.retweet_grapher

# with topic:
BIGQUERY_DATASET_NAME="impeachment_production" DIRPATH="graphs/example/abc123" TOPIC="#MAGA" TWEETS_START_AT="2020-01-10" TWEETS_END_AT="2020-01-11" BATCH_SIZE=125 VERBOSE_QUERIES="true" python -m app.retweet_graphs_v2.retweet_grapher

# without topic:
BIGQUERY_DATASET_NAME="impeachment_production" DIRPATH="graphs/example/3days" TWEETS_START_AT="2020-01-10"
TWEETS_END_AT="2020-01-14" BATCH_SIZE=5000 VERBOSE_QUERIES="true" python -m app.retweet_graphs_v2.retweet_grapher
```

### K Days Graphs

Constructing retweet graphs for each (daily) date range:

```sh
APP_ENV="prodlike" BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=10000 K_DAYS=1 START_DATE="2020-01-01" N_PERIODS=10 python -m app.retweet_graphs_v2.k_days.grapher
```

Loop through all graphs, download them locally, and generate a report of their sizes:

```sh
APP_ENV="prodlike" K_DAYS=1 START_DATE="2019-12-12" N_PERIODS=60 python -m app.retweet_graphs_v2.k_days.reporter
```

### K Days Bot Classification

Assigning bot scores for all users in each daily retweet graph, and upload CSV to Google Cloud Storage and BigQuery:

```sh
APP_ENV="prodlike" K_DAYS=1 START_DATE="2019-12-12" N_PERIODS=60 python -m app.retweet_graphs_v2.k_days.classifier

# SKIP_EXISTING="false" APP_ENV="prodlike" K_DAYS=1 START_DATE="2019-12-19" N_PERIODS=1 python -m app.retweet_graphs_v2.k_days.classifier
```

... and monitoring the results:

```sql
SELECT
  start_date
  ,count(distinct user_id) as over_50
  ,count(distinct case when bot_probability >= 0.6 THEN user_id END) as over_60
  ,count(distinct case when bot_probability >= 0.7 THEN user_id END) as over_70
  ,count(distinct case when bot_probability >= 0.8 THEN user_id END) as over_80
  ,count(distinct case when bot_probability >= 0.85 THEN user_id END) as over_85
  ,count(distinct case when bot_probability >= 0.9 THEN user_id END) as over_90
  ,count(distinct case when bot_probability >= 0.95 THEN user_id END) as over_95
FROM impeachment_production.daily_bot_probabilities
group by 1
order by 1
```

Downloading bot classifications:

```sh
APP_ENV="prodlike" K_DAYS=1 K_DAYS=1 START_DATE="2019-12-12" N_PERIODS=60 python -m app.retweet_graphs_v2.k_days.download_classifications
```
