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

## User Id Lookups

Looking up user ids:

```sh
# python app.retweet_graphs_v2.lookup_user_ids

DESTRUCTIVE_MIGRATIONS="true" BIGQUERY_DATASET_NAME="impeachment_production" python -m app.retweet_graphs_v2.lookup_user_ids
```

## More BigQuery Migrations

TODO


## Retweet Graphs

Testing graph storage:

```sh
python -m app.retweet_graphs_v2.graph_storage
```

Testing graph construction (mock graph):

```sh
DRY_RUN="true" python -m app.retweet_graphs_v2.retweet_grapher
```

Integration testing graph construction:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" DIRPATH="graphs/example" USERS_LIMIT=1000 BATCH
_SIZE=100 python -m app.retweet_graphs_v2.retweet_grapher
```

Constructing retweet graphs on the basis of user ids instead of screen names.

```sh
BIGQUERY_DATASET_NAME="impeachment_production" START_DATE="2020-01-01" K_DAYS=3 N_PERIODS=5 python -m app.retweet_graphs_v2.k_days_grapher
```
