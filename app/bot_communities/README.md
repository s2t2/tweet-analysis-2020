# Bot Communities

## BigQuery Migrations

First, when all daily classifications are complete, combine them and upload them to the "daily_bot_probabilities" table on BigQuery.

But in the meantime while those are in-progress, manually upload a single day's probabilities (2020-01-01) to a new table called "bot_probabilities_20200101". And then create a temporary "daily_bot_probabilities" table:

```sql
DROP TABLE IF EXISTS impeachment_production.daily_bot_probabilities;
CREATE TABLE IF NOT EXISTS impeachment_production.daily_bot_probabilities as (
    SELECT
        "2020-01-01" as start_date
        ,bp.screen_name as user_id
        ,bp.bot_probability
    FROM impeachment_production.bot_probabilities_20200101 bp
ORDER BY user_id
); -- this table only has 681 bots
```

## Detection

```sh
BIGQUERY_DATASET_NAME="impeachment_production" BOT_MIN="0.8" python -m app.bot_communities.bot_retweet_grapher.py
```
