
# Notes

## BigQuery Migrations

First, when all daily classifications are complete, combine them and upload them to the "daily_bot_probabilities" table on BigQuery.

But in the meantime while those are in-progress, manually upload a single day's probabilities (2020-01-01) to a new table called "bot_probabilities_20200101". And then create a temporary "daily_bot_probabilities_temp" table:

```sql
DROP TABLE IF EXISTS impeachment_production.daily_bot_probabilities_temp;
CREATE TABLE IF NOT EXISTS impeachment_production.daily_bot_probabilities_temp as (
    SELECT
        "2020-01-01" as start_date
        ,bp.screen_name as user_id
        ,bp.bot_probability
    FROM impeachment_production.bot_probabilities_20200101 bp
ORDER BY user_id
); -- this table only has 681 bots
```

After updating the classifier to automatically store results on BigQuery, we just need to manually insert the few days worth of classifications that were completed beforehand. Step one: add new table, select "from Google Cloud Storage", then browse to the given CSV file, and import into a new table named "bot_probabilities_YYYMMDD". Step two: add these ad-hoc daily tables into the main table where the rest are being collected:

```sql
INSERT INTO impeachment_production.daily_bot_probabilities (start_date, user_id, bot_probability) (
  SELECT "2019-12-12" as start_date, screen_name as user_id, bot_probability
  FROM impeachment_production.bot_probabilities_20191212 WHERE bot_probability > 0.5

  UNION ALL

  SELECT "2019-12-25" as start_date, screen_name as user_id, bot_probability
  FROM impeachment_production.bot_probabilities_20191225 WHERE bot_probability > 0.5

  UNION ALL

  SELECT "2020-01-01" as start_date, screen_name as user_id, bot_probability
  FROM impeachment_production.bot_probabilities_20200101 WHERE bot_probability > 0.5

  UNION ALL

  SELECT "2020-01-02" as start_date, screen_name as user_id, bot_probability
  FROM impeachment_production.bot_probabilities_20200102 WHERE bot_probability > 0.5
)

-- then OK to drop daily tables
DROP TABLE impeachment_production.bot_probabilities_20191212;
DROP TABLE impeachment_production.bot_probabilities_20191225;
DROP TABLE impeachment_production.bot_probabilities_20200101;
DROP TABLE impeachment_production.bot_probabilities_20200102;
```
