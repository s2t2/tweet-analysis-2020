# Toxicity Classification

## Toxicity Models

Using the Detoxify package for toxicity classification transformer models. For a list of available models and their descriptions, see the [Detoxify Docs](https://github.com/unitaryai/detoxify#prediction).

  + `original`: `bert-base-uncased` / Toxic Comment Classification Challenge
  + `unbiased`: `roberta-base` / Unintended Bias in Toxicity Classification


## Database Migrations

```sql
SELECT
  count(distinct status_id) as status_count -- 67666557
  ,count(distinct user_id) as user_count  -- 3600545
  ,count(distinct status_text) as text_count -- 13539079
FROM `tweet-collector-py.impeachment_production.tweets`

```

Of 67M tweets, only 13M unique status texts, so let's just operate on those (while making sure we can still join via status_id).

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.status_texts`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.status_texts` as (
    SELECT
        ROW_NUMBER() OVER() status_text_id
        ,status_text
        ,status_ids
        ,status_count
    FROM (
        SELECT
            status_text
            ,array_agg(cast(status_id as int64)) as status_ids
            ,count(distinct status_id) as status_count
        FROM `tweet-collector-py.impeachment_production.tweets`
        GROUP BY 1
        --ORDER BY 3 DESC
        --LIMIT 1000
    )
);
```

Making sure we can re-join later (although this query is super / too slow hmmm):

```sql
WITH t as (
    SELECT
        cast(status_id as int64) as status_id
        ,status_text
    FROM  `tweet-collector-py.impeachment_production.tweets`
)

SELECT
  txt.status_text_id
  ,txt.status_text
  --,txt.status_ids
  ,txt.status_count
  ,t.status_id
FROM `tweet-collector-py.impeachment_production.status_texts` txt
JOIN t on t.status_id in unnest(txt.status_ids)
```

This is not good.

How bad would it be to save 67M inserts back into a row per status table structure instead? This would make the analysis query joins much easier later. But saving the 67M records would still be five times slower than necessary. Let's try making a join table - maybe BQ will be able to join faster using the join table than joining on nested array values.


```sql
-- row per status_text_id, per status_id (essentially linking the texts to the statuses)
--
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.statuses_texts`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.statuses_texts` as (
    SELECT status_text_id, status_id
    FROM `tweet-collector-py.impeachment_production.status_texts`,
    UNNEST(status_ids) as status_id
)

```

Can re-join fast?

```sql
SELECT DISTINCT
  txt.status_text_id
  ,txt.status_text
  --,txt.status_ids
  ,txt.status_count
  ,st.status_id
FROM `tweet-collector-py.impeachment_production.status_texts` txt
JOIN `tweet-collector-py.impeachment_production.statuses_texts` st ON st.status_text_id = txt.status_text_id
WHERE txt.status_text_id = 308
LIMIT 10000
```

Yeah this works.


So we can store one record of scores per text.

Migrate table for storing toxicity scores (where "original" references the toxicity model name):

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original` (
    status_text_id INT64,
    identity_hate FLOAT64,
    insult FLOAT64,
    obscene FLOAT64,
    severe_toxicity FLOAT64,
    threat FLOAT64,
    toxicity FLOAT64
);
```


So the query to figure out which texts haven't yet already been looked up is:

```sql
SELECT DISTINCT
  txt.status_text_id
  ,txt.status_text
  --,txt.status_ids
  --,txt.status_count
FROM `tweet-collector-py.impeachment_production.status_texts` txt
LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original` scores ON scores.status_text_id = txt.status_text_id
WHERE scores.status_text_id IS NULL
LIMIT 10000
```


Development Database Setup:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.status_texts`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.status_texts` as (
    SELECT
        ROW_NUMBER() OVER() status_text_id
        ,status_text
        ,status_ids
        ,status_count
    FROM (
        SELECT
            status_text
            ,array_agg(cast(status_id as int64)) as status_ids
            ,count(distinct status_id) as status_count
        FROM `tweet-collector-py.impeachment_production.tweets`
        GROUP BY 1
        --ORDER BY 3 DESC
        LIMIT 1000
    )
);
```

```sql
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.statuses_texts`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.statuses_texts` as (
--     SELECT status_text_id, status_id
--     FROM `tweet-collector-py.impeachment_production.status_texts`,
--     UNNEST(status_ids) as status_id
-- );
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.toxicity_scores_original`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.toxicity_scores_original` (
    status_text_id INT64,
    toxicity FLOAT64
    severe_toxicity FLOAT64,
    obscene FLOAT64,
    threat FLOAT64,
    insult FLOAT64,
    identity_hate FLOAT64,
);
```

## Usage

```sh
python -m app.toxicity.scorer

MODEL_NAME="original" python -m app.toxicity.scorer
MODEL_NAME="unbiased" python -m app.toxicity.scorer

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10000 BATCH_SIZE=1500 python -m app.toxicity.scorer
```


```sh
python -m app.toxicity.scorer_in_batches

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10000 BATCH_SIZE=500 python -m app.toxicity.scorer_in_batches

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=100 BATCH_SIZE=30 python -m app.toxicity.score_in_batches


LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.score_in_batches
```
