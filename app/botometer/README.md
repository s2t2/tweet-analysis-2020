
# Botometer Sample

References:
  + https://github.com/IUNetSci/botometer-python
  + https://rapidapi.com/OSoMe/api/botometer-pro/pricing

## Constraints

We are limited by the Botometer Pro Plan to 2,000 requests / day.

## Goals

Ideally it would be nice to score 3.6M users. Otherwise score all the bots (24,150) and the same number of humans (~50K total). Or at least take a sample of 2,000 of each (4K total).

## Plan

Let's move forward with a sample of 2,000 from each. We'll do multiple smaller samples, to stay under the limit 2K per day. If we do a total sample of 1.5K per day, it will only take two or three days to perform the lookups.

To prevent duplicate lookups, we'll cross reference the table holding the stored lookups and exlude any users already looked-up. This way we can run the script over again once per day with small sample sizes.

Upon completion, we'll have the job sleep for a day and restart. If we leave it for a week we could get the larger ~50K sample size.

## Botometer Data Dictionary

Interpreting the botometer scores...

**Meanings of the elements in the response:**

  + `user`: Twitter user object (from the user) plus the language inferred from majority of tweets
  + `raw scores`: bot score in the [0,1] range, both using English (all features) and Universal (language-independent) features; in each case we have the overall score and the sub-scores for each bot class (see below for subclass names and definitions)
display scores: same as raw scores, but in the [0,5] range
  + `cap`: conditional probability that accounts with a score equal to or greater than this are automated; based on inferred language

**Meanings of the bot type scores:**

 + `fake_follower`: bots purchased to increase follower counts
 + `self_declared`: bots from botwiki.org
 + `astroturf`: manually labeled political bots and accounts involved in follow trains that systematically delete content
 + `spammer`: accounts labeled as spambots from several datasets
 + `financial`: bots that post using cashtags
 + `other`: miscellaneous other bots obtained from manual annotation, user feedback, etc.

## BQ Migrations

Setup tables to store lookups. We are storing raw scores for each type (english lang / universal, etc.).

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_development.botometer_scores`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.botometer_scores` (
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.botometer_scores`;
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.botometer_scores` (
    user_id INT64,
    lookup_at TIMESTAMP,
    error_message STRING,
    score_type STRING, -- english / universal
    cap FLOAT64,
    astroturf FLOAT64,
    fake_follower FLOAT64,
    financial FLOAT64,
    other FLOAT64,
    overall FLOAT64,
    self_declared FLOAT64,
    spammer FLOAT64,
);
```

Copy user details table to development database, if not already there, to enable running in development:

```sql
CREATE TABLE `tweet-collector-py.impeachment_development.user_details_v20210806_slim` as (
  SELECT *
  FROM `tweet-collector-py.impeachment_production.user_details_v20210806_slim`
)
```

## Botometer Lookups

Use the `LIMIT` to set the size of the number of bots and humans, respectively. Sample size will be 2x the limit.

```sh
python -m app.botometer.sampler

# max of 1.5K per day:
LIMIT=750 python -m app.botometer.sampler
```


## Comparison

After lookups are complete, get a list of our bot classifications, and the corresponding botometer scores, so we can compare them:

```sql
SELECT
    u.user_id
    ,u.is_bot
    ,u.is_q ,u.opinion_community
    ,u.avg_fact_score, u.avg_toxicity, u.created_on

    --bom.user_id
    ,bom.score_type as bom_score_type
    ,count(distinct bom.lookup_at) as bom_lookup_count
    ,avg(bom.cap) as bom_cap
    ,avg(bom.astroturf) as bom_astroturf
    ,avg(bom.fake_follower) as bom_fake_follower
    ,avg(bom.financial) as bom_financial
    ,avg(bom.other) as bom_other
    ,avg(bom.overall) as bom_overall
    ,avg(bom.self_declared) as bom_self_declared
    ,avg(bom.spammer) as bom_spammer
FROM `tweet-research-shared.impeachment_2020.botometer_scores` bom
JOIN `tweet-research-shared.impeachment_2020.user_details_v20210806_slim` u ON bom.user_id = u.user_id -- 8683
WHERE bom.score_type = 'english' -- 7,566 users with english scores
GROUP BY 1,2,3,4,5,6,7,8
-- HAVING lookup_count > 1 -- 333 users have multiple lookups, so we're going to average them instead of drop them
```

See [notebook](Botometer_Score_Comparisons.ipynb) for ROC - AUC results.

## Updated User Details Table

Making a new version of the table with english scores only and a row per user, for easier joins to the user details table:

```sql
CREATE TABLE `tweet-collector-py.impeachment_production.botometer_scores_v2` as (
  SELECT
        bom.user_id
        --,bom.score_type as bom_score_type
        ,count(distinct bom.lookup_at) as bom_lookup_count
        ,avg(bom.cap) as bom_cap
        ,avg(bom.astroturf) as bom_astroturf
        ,avg(bom.fake_follower) as bom_fake_follower
        ,avg(bom.financial) as bom_financial
        ,avg(bom.other) as bom_other
        ,avg(bom.overall) as bom_overall
        ,avg(bom.self_declared) as bom_self_declared
        ,avg(bom.spammer) as bom_spammer
    FROM `tweet-collector-py.impeachment_production.botometer_scores` bom 
    WHERE bom.score_type = 'english' -- 7,566 users with english scores
    GROUP BY 1
    -- LIMIT 10
)
```

```sql
CREATE TABLE `tweet-collector-py.impeachment_production.user_details_v20240128_slim`  as (

    SELECT 
      u.user_id, u.created_on, u.screen_name_count, u.screen_names
      ,u.status_count, u.rt_count
      ,u.is_bot, u.bot_rt_network
      ,u.opinion_community, u.avg_score_lr, avg_score_nb, avg_score_bert

      , u.is_q, u.q_status_count 
      , u.follower_count, u.follower_count_b, u.follower_count_h
      , u.friend_count, u.friend_count_b, u.friend_count_h

      ,u.avg_toxicity, u.avg_severe_toxicity, u.avg_insult, u.avg_obscene, u.avg_threat, u.avg_identity_hate
      ,u.fact_scored_count, u.avg_fact_score
      
      ,bom.bom_lookup_count ,bom.bom_astroturf, bom.bom_overall, bom.bom_cap 
      ,bom.bom_fake_follower, bom.bom_financial, bom.bom_other, bom.bom_self_declared, bom.bom_spammer

    FROM `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u 
    LEFT JOIN `tweet-collector-py.impeachment_production.botometer_scores_v2` bom ON bom.user_id = u.user_id
    -- WHERE bom.user_id IS NOT NULL
    -- LIMIT 10
);
```
