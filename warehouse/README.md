# Warehouse Migrations

In addition to the [user details table migration](/app/news/README.md), copying over the following tables into the shared environment:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.retweets_v2` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.retweets_v2`
    --LIMIT 10
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.domain_fact_scores` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.domain_fact_scores`
    -- LIMIT 10
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.recollected_statuses` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.recollected_statuses`
    -- LIMIT 10
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.recollected_status_urls` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
    -- LIMIT 10
 );
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.recollected_status_url_domains` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.recollected_status_url_domains`
    -- LIMIT 10
);
```


```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.tweets_v2` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.tweets_v2`
    -- LIMIT 10
);
```

This table is 25 GB so let's just port over a preview for now until we have a more specific use case:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.active_user_friends_flat_v2_preview` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.active_user_friends_flat_v2`
    LIMIT 100000
);
```
