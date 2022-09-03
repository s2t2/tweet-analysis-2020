# Warehouse Migrations

In addition to the [user details table migration](/app/news/README.md), copying over the following tables into the shared environment:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.topics` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.topics`
    -- LIMIT 10
 );
```


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

Second round of additions:


```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.tweet_toxicity_scores` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.tweet_toxicity_scores`
    -- LIMIT 5
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.nlp_v2_predictions_combined_v2` as (
    SELECT

        user_id	-- INTEGER	NULLABLE
        ,screen_name	-- STRING	NULLABLE
        ,user_created_at	-- TIMESTAMP	NULLABLE
        ,cast(status_id	as int64) as status_id -- STRING	NULLABLE
        ,is_rt-- BOOLEAN	NULLABLE
        ,created_at		--  TIMESTAMP	NULLABLE
        ,status_text		-- STRING	NULLABLE
        ,score_lr		-- INTEGER	NULLABLE
        ,score_nb		-- INTEGER	NULLABLE
        ,score_bert

    FROM `tweet-collector-py.impeachment_production.nlp_v2_predictions_combined_v2`
    -- LIMIT 5
);
```

Hashtag and mention related tables:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.profile_tags_v2_flat` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.profile_tags_v2_flat`
    -- LIMIT 5
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.status_tags_v2_flat` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.status_tags_v2_flat`
    -- LIMIT 5
);
```

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.status_mentions_v2_flat` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.status_mentions_v2_flat`
    -- LIMIT 5
);
```


Labeled tweets, for use in model training:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.2_community_labeled_tweets` as (
    SELECT user_id, community_id as sentiment_label, status_id, status_text, created_at
    FROM `tweet-collector-py.impeachment_production.2_community_labeled_tweets`
);
```


Daily bot probabilities:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.daily_bot_probabilities` as (
  SELECT *
  FROM `tweet-collector-py.impeachment_production.daily_bot_probabilities`
);
```

User profiles:

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.user_profiles_v2` as (
  SELECT *
  FROM `tweet-collector-py.impeachment_production.user_profiles_v2`
)
```




Botometer scores:


```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.botometer_scores` as (
  SELECT *
  FROM `tweet-collector-py.impeachment_production.botometer_scores`
)
```
