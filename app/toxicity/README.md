# Toxicity Classification

## Database Migrations

Migrations:

```sql
-- SELECT
--   count(distinct status_id) as status_count -- 67666557
--   , count(distinct user_id) as user_count  -- 3600545
--   ,count(distinct status_text) as text_count -- 13539079
-- FROM `tweet-collector-py.impeachment_production.tweets`

-- of 67M tweets, only 13M unique status texts
-- so let's just operate on those
-- while making sure we can still join via status_id

DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.tweet_texts`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.tweet_texts` as (

    SELECT
        status_text
        ,string_agg(status_id, ", ") as status_ids_str
        ,array_agg(cast(status_id as int64)) as status_ids
        ,count(distinct status_id) as status_count
    FROM `tweet-collector-py.impeachment_production.tweets`
    GROUP BY 1
    ORDER BY 3 DESC
    LIMIT 10

);
```

Making sure we can re-join later (although this query is super / too slow hmmm):

```sql
SELECT txt.status_text, txt.status_ids, txt.status_count , t.status_id
FROM `tweet-collector-py.impeachment_production.tweet_texts` txt
JOIN `tweet-collector-py.impeachment_production.tweets` t on cast(t.status_id as int64) in unnest(txt.status_ids)
```




## Usage

For a list of available models and their descriptions, see the [Detoxify Docs](https://github.com/unitaryai/detoxify#prediction).

  + `original`: `bert-base-uncased` / Toxic Comment Classification Challenge
  + `unbiased`: `roberta-base` / Unintended Bias in Toxicity Classification

```sh
MODEL_NAME="original" python -m app.toxicity.scorer

MODEL_NAME="unbiased" python -m app.toxicity.scorer
```
