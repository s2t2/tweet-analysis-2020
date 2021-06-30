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

## Investigation

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

### Benchmarking Prediction Batch Sizes

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

## Usage


```sh
LIMIT=10 BATCH_SIZE=3 python -m app.toxicity.scorer


MODEL_NAME="original" BIGQUERY_DATASET_NAME="impeachment_production" LIMIT=50000 BATCH_SIZE=1000 python -m app.toxicity.scorer
```
