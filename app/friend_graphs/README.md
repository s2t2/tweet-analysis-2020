
# Friend Graphs

In order to analyze Twitter user network graphs, we'll construct a `networkx` Graph object and make use of some of its built-in analysis capabilities.

When assembling this network graph object, one option is to stream the user data directly from BigQuery:

```sh
# incremental graph construction (uses more incremental memory):
python -m app.friend_graphs.bq_grapher
# BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="true" BATCH_SIZE=1000 python app.friend_graphs.bq_grapher

# graph construction from complete edges list (uses less incremental memory):
python -m app.friend_graphs.bq_list_grapher
# BIGQUERY_DATASET_NAME="impeachment_development" DRY_RUN="false" python -m app.friend_graphs.bq_list_grapher
```

However, depending on the size of the graph, that approach might run into memory errors. So another option is to query the data from the local PostgreSQL database. First, ensure you've setup and populated a remote Heroku PostgreSQL database using the "Local Database Setup" and "Local Database Migration" instructions above. After the database is ready, you can try to assemble the network graph object from PostgreSQL data:

```sh
# graph construction from complete edges list (uses less incremental memory):
python -m app.friend_graphs.psycopg_list_grapher
# USERS_LIMIT=10000 BATCH_SIZE=1000 DRY_RUN="true" python -m app.friend_graphs.psycopg_list_grapher
# USERS_LIMIT=100000 BATCH_SIZE=1000 DRY_RUN="false" python -m app.friend_graphs.psycopg_list_grapher
```

> NOTE: you might be unable to create graph objects to cover your entire user dataset, so just make the largest possible given the memory constraints of the computers and servers available to you by trying to get the `USERS_LIMIT` as large as possible.

## Topic Graphs

The graphs are very large, so how about we create a few different smaller topic-specific graphs:

```sh
# assemble right-leaning conversation graph:
BIGQUERY_DATASET_NAME="impeachment_production" USERS_LIMIT=1000 BATCH_SIZE=100 TOPIC="#MAGA" python -m app.friend_graphs.bq_topic_grapher

# assemble left-leaning conversation graph:
BIGQUERY_DATASET_NAME="impeachment_production" USERS_LIMIT=1000 BATCH_SIZE=100 TOPIC="#ImpeachAndConvict" python -m app.friend_graphs.bq_topic_grapher
```




<hr>






# Friend Graph Notes

## Downloading User Friends

Transferring 10K users from BigQuery development database to a local PostgreSQL database, to make subsequent analysis easier (prevent unnecessary future network requests):

```sh
DESTRUCTIVE_PG=true BATCH_SIZE=100 python -m app.pg_pipeline.user_friends
```

Benchmarking different batch sizes:

Users | Batch Size | Duration (seconds)
--- | --- | ---
10000 | Individual| 214
10000 | 50 | 182
10000 | 100 (first run) | 159
10000 | 100 (second run) | 171
10000 | 200 | 162
10000 | 500 | 208
10000 | 1000 | 227

Choosing optimal batch size of around 100.

Transferring all 3.6M users from the BigQuery production database:

```sh
BIGQUERY_DATASET_NAME="impeachment_production" DESTRUCTIVE_PG=true BATCH_SIZE=100 python -m app.pg_pipeline.user_friends
```

Users | Batch Size | Duration (seconds)
--- | --- | ---
3636616 | 100 | 20151

Making various smaller versions of the user friends table, for development purposes:

```sql
CREATE TABLE user_friends_dev as (
    SELECT * FROM user_friends LIMIT 100000
);
```

Copying / backing-up the user friends table as "user_friends_clone".

Identifying screen names that have multiple user ids (may need to be excluded / cleaned from the dataset):

```sql
SELECT
    screen_name
    ,count(distinct id) as row_count
FROM user_friends
GROUP BY 1
HAVING count(distinct id) > 1
ORDER BY 2 desc;

-- > 612 screen names
```


Making an even smaller (and cleaner) version of the user friends table, for testing purposes (with 10k, 100k):

```sql
CREATE TABLE user_friends_10k as (
  SELECT
    uf.id
    ,uf.user_id
    ,uf.screen_name
    ,uf.friend_count
    ,uf.friend_names
  FROM user_friends_dev uf
  LEFT JOIN (
      -- screen names with multiple user ids
      SELECT
          screen_name
          -- user_id
          , count(distinct id) as row_count
      FROM user_friends_dev
      GROUP BY 1
      HAVING count(distinct id) > 1
      ORDER BY 2 desc
  ) subq ON subq.screen_name = uf.screen_name
  WHERE subq.screen_name IS NULL -- filters out dups
  LIMIT 10000
);
CREATE INDEX tenkay_id ON user_friends_10k USING btree(id);
CREATE INDEX tenkay_uid ON user_friends_10k USING btree(user_id);
CREATE INDEX tenkay_sn ON user_friends_10k USING btree(screen_name);

-- CREATE INDEX hunkay_id ON user_friends_100k USING btree(id);
-- CREATE INDEX hunkay_uid ON user_friends_100k USING btree(user_id);
-- CREATE INDEX hunkay_sn ON user_friends_100k USING btree(screen_name);
```

## Friend Graph Construction Results

Initial attempts to assemble graph object for production dataset (3.6M users) ends up crashing due to memory issues.

The largest friend graph we've been able to construct so far is from only 50K users of the 3.6M users in our dataset (job id: "2020-05-30-0338"). That friend graph has 8.7M nodes and 27.3M edges, and requires 19GB of memory to complete. These memory requirements pushed the largest Heroku server to its limits.

These memory constraints require us to either further optimize memory usage, get access to much larger servers, or deem acceptable the graph size we do have.

## Conversation Topic Graphs

Constructing separate graph objects for different topics of conversation across different periods of time (e.g. the graph for discussion of the topic ABC during the week of XYZ)...

Assembled right-leaning graph (job `2020-06-07-2049`):

```js
{
  "app_env": "development",
  "job_id": "2020-06-07-2049",
  "dry_run": false,
  "batch_size": 100,
  "dataset_address": "tweet-collector-py.impeachment_production",
  "destructive": false,
  "verbose": false,
  "conversation": {
    "users_limit": 1000,
    "topic": "#MAGA",
    "start_at": "2019-01-15 01:00:00",
    "end_at": "2020-01-30 01:00:00"
  }
}
```

Assembled left-leaning graph (job `2020-06-07-2056`):

```js
{
  "app_env": "development",
  "job_id": "2020-06-07-2056",
  "dry_run": false,
  "batch_size": 100,
  "dataset_address": "tweet-collector-py.impeachment_production",
  "destructive": false,
  "verbose": false,
  "conversation": {
    "users_limit": 1000,
    "topic": "#ImpeachAndConvict",
    "start_at": "2019-01-15 01:00:00",
    "end_at": "2020-01-30 01:00:00"
  }
}
```
