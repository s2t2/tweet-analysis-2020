# Toxicity Classification

## Notes

### Toxicity Models

Using the Detoxify package for toxicity classification transformer models. For a list of available models and their descriptions, see the [Detoxify Docs](https://github.com/unitaryai/detoxify#prediction).

  + `original`: `bert-base-uncased` / Toxic Comment Classification Challenge
  + `unbiased`: `roberta-base` / Unintended Bias in Toxicity Classification

### Comparing Models

There are some differences between the two main toxicity models. We'll probably want the results of both unless we have a preference for methodological reasons.

```sh
(tweet-analyzer-env-38)  --->> python -m app.toxicity.investigate_models

#> ----------------
#>
#> TEXT: 'RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.000993     1.004200e-04  0.000182  0.000117  0.000180       0.000141  original
#> 1  0.000588     9.500000e-07  0.000040  0.000026  0.000216            NaN  unbiased
#>
#> ----------------
#>
#> TEXT: 'RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.126401         0.000225  0.001830  0.000507  0.009287       0.001832  original
#> 1  0.367150         0.000003  0.000419  0.000169  0.296279            NaN  unbiased
#> ----------------
#>
#> TEXT: 'RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.000855     1.146300e-04  0.000166  0.000138  0.000186       0.000157  original
#> 1  0.000636     8.700000e-07  0.000041  0.000025  0.000246            NaN  unbiased
#>
#> ----------------
#>
#> TEXT: 'RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.001845         0.000100  0.000289  0.000095  0.000234       0.000162  original
#> 1  0.000909         0.000002  0.000063  0.000141  0.000227            NaN  unbiased
```

Looks like the unbiased model has different class names actually:

```sh
'toxicity',
'severe_toxicity',
'obscene',
'identity_attack',
'insult',
'threat',
'sexual_explicit'
```

### Benchmarking Batch Sizes

The models are capable of scoring many texts at a time. But how many is most efficient?

```sh
python -m app.toxicity.investigate_benchmarks

#> ---------------------
#> MODEL: ORIGINAL
#> ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
#> ---------------------
#> PROCESSED 1 ITEMS IN 0.06 SECONDS (16.67 items / second)
#> ---------------------
#> PROCESSED 10 ITEMS IN 0.21 SECONDS (47.62 items / second)
#> ---------------------
#> PROCESSED 100 ITEMS IN 1.81 SECONDS (55.25 items / second)
#> ---------------------
#> PROCESSED 1000 ITEMS IN 17.49 SECONDS (57.18 items / second)
#> ---------------------
#> PROCESSED 10000 ITEMS IN 192.87 SECONDS (51.85 items / second)
#> ---------------------
```

The highest processing rate for the toxicity model seems to be around 1,000 texts at a time (50 per second, 300 per minute, 180K per hour, 4.32M per day). This can work. We'd need to run server for like 3 days. Very reasonable.




## Setup

### Database Migrations

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
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt` (
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt_slow`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt_slow` (
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
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased_ckpt_slow`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.toxicity_scores_unbiased_ckpt_slow` (
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

So the query to figure out which texts haven't yet already been looked up is:

```sql
SELECT DISTINCT txt.status_text_id ,txt.status_text
FROM `tweet-collector-py.impeachment_production.status_texts` txt
--LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original` scores
--LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt` scores
LEFT JOIN `tweet-collector-py.impeachment_production.toxicity_scores_original_ckpt_slow` scores
    ON scores.status_text_id = txt.status_text_id
WHERE scores.status_text_id IS NULL
LIMIT 10000;
```


## Usage

### Detoxify Models

Running the scorer (ideal batch size is 1,000):

```sh
LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer

MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer

MODEL_NAME="unbiased" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer


MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=25000 BATCH_SIZE=1000 python -m app.toxicity.scorer
```

> NOTE: you probably want to run multithreaded though...

Running multithreaded:

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

... async:

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
heroku config:set MODEL_NAME="original" -r heroku-6
```

Deploy:

```sh
git push heroku-5 tox:master -f
git push heroku-6 tox:master -f
```


The deploy will fail if the compressed size of all package dependencies is too big (>500MB). The detoxify package was way too big itslef (800MB), so we loaded its component torch dependencies directly, but with a smaller size (for CPUs, don't need GPU support). And we also have to temporarily comment-out some of the other packages (like some dataviz packages we're not using for this specific process) in the requirements.txt file. And now the deploy works.

Writing a new scorer to work with this dependency situation (see "Detoxify Model Checkpoints" section above.)

Then turn on the "toxicity_checkpoint_scorer" dyno (see Procfile).

Memory exceeded, turning up to ... "Standard-2X" size. Decreasing batch size to ... 20. Decreasing limit to 20K. Seems to be running consistently.

> NOTE: after starting this process on server 5 (using "_ckpt" tables), we're locking dependencies for reproducibility, and re-running the process on server 6 (using the toxicity_checkpoint_scorer_async approach if possible)
