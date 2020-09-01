# Natural Language Processing

We can use multiple approaches for training our classifiers - fetching tweet embeddings from an external API, or creating our own.

## Prep

Migrate BQ tables:

```sql
DROP TABLE IF EXISTS impeachment_production.statuses;
CREATE TABLE impeachment_production.statuses as (
  SELECT DISTINCT status_id, user_id, status_text, created_at
  FROM impeachment_production.tweets
);

SELECT count(status_id) as row_count ,count(distinct status_id) as id_count
FROM impeachment_production.statuses
-- same number, looks good. row per unique status. let's go...
```

```sql
DROP TABLE IF EXISTS impeachment_production.partitioned_statuses;
CREATE TABLE impeachment_production.partitioned_statuses as (
  SELECT
    cast(status_id as INT64) as status_id
    ,cast(user_id as INT64) as user_id
    ,status_text
    ,created_at
    ,rand() as partition_val -- a decimal between 0 and 1
  FROM impeachment_production.tweets
  GROUP BY 1,2,3,4
);

SELECT
  case when partition_val between 0.0 and 0.1 then 1
       when partition_val between 0.1 and 0.2 then 2
       when partition_val between 0.2 and 0.3 then 3
       when partition_val between 0.3 and 0.4 then 4
       when partition_val between 0.4 and 0.5 then 5
       when partition_val between 0.5 and 0.6 then 6
       when partition_val between 0.6 and 0.7 then 7
       when partition_val between 0.7 and 0.8 then 8
       when partition_val between 0.8 and 0.9 then 9
       when partition_val between 0.9 and 1.0 then 10
  end partition_id

  ,count(distinct status_id) as status_count

FROM impeachment_production.partitioned_statuses
GROUP BY 1
ORDER BY 1

-- 6,763,194 rows per partition
```

```sql
DROP TABLE IF EXISTS impeachment_production.basilica_embeddings;
CREATE TABLE impeachment_production.basilica_embeddings (
    status_id INT64,
    embedding ARRAY<FLOAT64>
);
```

## Basilica Embeddings

Run the basilica service to test the credentials:

```sh
python -m app.basilica_service
```

Then fetch embeddings for each status text and store them in an "embeddings" table on BigQuery:

```sh
BATCH_SIZE=10 LIMIT=105 python -m app.nlp.basilica_embedder
```

This will take a while, so consider using the parallel processing version instead:

```sh
#LIMIT=100000 BATCH_SIZE=1000 MAX_THREADS=10 python -m app.nlp.basilica_embedder_parallel

APP_ENV="prodlike" MIN_VAL="0.0" MAX_VAL="0.1" LIMIT=500000 BATCH_SIZE=1000 MAX_THREADS=10 python -m app.nlp.basilica_embedder_parallel
APP_ENV="prodlike" MIN_VAL="0.1" MAX_VAL="0.2" LIMIT=500000 BATCH_SIZE=1000 MAX_THREADS=10 python -m app.nlp.basilica_embedder_parallel
```
