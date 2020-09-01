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
python -m app.nlp.fetch_basilica_embeddings
```
