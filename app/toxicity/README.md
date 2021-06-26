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

How bad would it be to save 67M inserts back into a row per status table structure instead? This would make the analysis query joins much easier later.

Migrate table for storing toxicity scores (where "original" references the toxicity model name):

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.status_toxicity_scores_original`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.status_toxicity_scores_original` (
    status_id INT64,
    identity_hate FLOAT64,
    insult FLOAT64,
    obscene FLOAT64,
    severe_toxicity FLOAT64,
    threat FLOAT64,
    toxicity FLOAT64
);
```

## Usage

```sh
python -m app.toxicity.scorer

MODEL_NAME="original" python -m app.toxicity.scorer
MODEL_NAME="unbiased" python -m app.toxicity.scorer

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" BATCH_SIZE=1500 python -m app.toxicity.scorer
```
