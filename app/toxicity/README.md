# Toxicity Classification

## [Notes](NOTES.md)

## Database Migrations

Of 67M tweets, there are only 13M unique status texts. To avoid unnecessary processing, we'll score only the unique texts.

```sql
SELECT
  count(distinct status_id) as status_count -- 67666557
  ,count(distinct user_id) as user_count  -- 3600545
  ,count(distinct status_text) as text_count -- 13539079
FROM `tweet-collector-py.impeachment_production.tweets`
```

So we'll want a table of unique texts ("status_texts"), and the ability to join them back via `status_id`. If we nest these `status_ids` as an array in the texts table, we aren't able to join back later (BQ has a hard time with the joins). So instead we'll make a separate join table ("statuses_texts").

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
    )
);

DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.statuses_texts`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.statuses_texts` as (
    SELECT status_text_id, status_id
    FROM `tweet-collector-py.impeachment_production.status_texts`,
    UNNEST(status_ids) as status_id
)
```

We'll make a table for storing toxicity scores from each model (where "original" references the toxicity model name and "ckpt" references scores from models reconstituted from checkpoints):

```sql
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt` (
    status_text_id INT64,
    toxicity FLOAT64,
    severe_toxicity FLOAT64,
    obscene FLOAT64,
    threat FLOAT64,
    insult FLOAT64,
    identity_hate FLOAT64,
);

-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased` (
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased_ckpt`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased_ckpt` (
--     status_text_id INT64,
--     toxicity FLOAT64,
--     severe_toxicity FLOAT64,
--     obscene FLOAT64,
--     identity_attack FLOAT64,
--     insult FLOAT64,
--     threat FLOAT64,
--     sexual_explicit FLOAT64
-- );
```

> FYI: the different models have different class / column names

A query to figure out which texts haven't yet already been looked up is:

```sql
SELECT DISTINCT txt.status_text_id ,txt.status_text
FROM `tweet-collector-py.impeachment_production.status_texts` txt
--LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original` scores
LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt` scores
    ON scores.status_text_id = txt.status_text_id
WHERE scores.status_text_id IS NULL
LIMIT 10000;
```


## Usage

We started to use the model provided by the detoxify package (see "Detoxify Models" section below). But that package is too large to be installed on the server (see "Deployment" section below), so we ended up re-constituting the same model but using lighter dependencies (see "Detoxify Model Checkpoints" section below).

### Detoxify Models

> NOTE: this scorer is DEPRECATED in favor of the checkpoint scorer (see "Detoxify Model Checkpoints" section below)...

Running the scorer:

```sh
LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer

MODEL_NAME="unbiased" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer


MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=25000 BATCH_SIZE=1000 python -m app.toxicity.scorer
```

... async / multithreaded:

```sh
LIMIT=500 BATCH_SIZE=100 MAX_THREADS=5 python -m app.toxicity.scorer_async

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_development" LIMIT=500 BATCH_SIZE=100  MAX_THREADS=5 python -m app.toxicity.scorer_async

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=500 BATCH_SIZE=100  MAX_THREADS=5 python -m app.toxicity.scorer_async
```

### Detoxify Model Checkpoints


Use toxicity models reconstituted from checkpoints:

```sh
BIGQUERY_DATASET_NAME="impeachment_development" LIMIT=100 BATCH_SIZE=10 python -m app.toxicity.checkpoint_scorer
```

... async / multithreaded:

```sh
BIGQUERY_DATASET_NAME="impeachment_development" LIMIT=100 BATCH_SIZE=10 MAX_THREADS=10 python -m app.toxicity.checkpoint_scorer_async
```


## Testing

```sh
APP_ENV="test" pytest test/test_toxicity_*
```

## Deployment

Using server #5 for original model.

Config:

```sh
heroku config:set MODEL_NAME="original" -r heroku-5
heroku config:set LIMIT="20000" -r heroku-5
heroku config:set BATCH_SIZE="20" -r heroku-5

#heroku config:set MODEL_NAME="original" -r heroku-6
#heroku config:set LIMIT="50000" -r heroku-6
#heroku config:set BATCH_SIZE="20" -r heroku-6
#heroku config:set MAX_THREADS="10" -r heroku-6
```

Deploy:

```sh
git push heroku-5 tox:master -f
#git push heroku-6 tox:master -f
```


The deploy will fail if the compressed size of all package dependencies is too big (>500MB). The detoxify package was way too big itslef (800MB), so we loaded its component torch dependencies directly, but with a smaller size (for CPUs, don't need GPU support). And we also have to temporarily comment-out some of the other packages (like some dataviz packages we're not using for this specific process) in the requirements.txt file. And now the deploy works.

Writing a new scorer to work with this dependency situation (see "Detoxify Model Checkpoints" section above.)

Then turn on the "toxicity_checkpoint_scorer" dyno (see Procfile).

Memory exceeded, turning up to ... "Standard-2X" size. Decreasing batch size to ... 20. Decreasing limit to 20K. Seems to be running consistently.
