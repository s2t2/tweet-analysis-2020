# Deploying


Whoah it's been a while. What servers do we have? OK let's choose one (-r heroku-9  / -a impeachment-tweet-analysis-9).

## Configuration

Reconfig vars:

```sh
heroku config:set RAPID_API_KEY="___________"  -r heroku-9
heroku config:set LIMIT=750  -r heroku-9

heroku config:set TWITTER_API_KEY="___________"-r heroku-9
heroku config:set TWITTER_API_KEY_SECRET="___________" -r heroku-9
heroku config:set TWITTER_ACCESS_TOKEN="___________" -r heroku-9
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="___________" -r heroku-9
```

Add `botometer_sampler` job to Procfile (see [Procfile](/Procfile)).

## Migration

Perform [migrations](README.md#bq-migrations) on the production BQ database.

## Deploying

```sh
git push heroku-9 botometer:main
```

```sh
heroku logs --tail -r heroku-9
```

Turn on the `botometer_sampler` job.

## Monitoring


```sql
-- bom_lookups_v3.csv
SELECT
    u.user_id
      ,u.is_bot, u.is_q, u.opinion_community
      ,u.avg_fact_score, u.avg_toxicity, u.created_on

    ,bom.score_type
    ,count(distinct bom.lookup_at) as lookup_count
    ,any_value(bom.error_message) as lookup_error

    ,avg(bom.cap) as cap
    ,avg(bom.astroturf) as astroturf
    ,avg(bom.fake_follower) as fake_follower
    ,avg(bom.financial) as financial
    ,avg(bom.other) as other
    ,avg(bom.overall) as overall
    ,avg(bom.self_declared) as self_declared
    ,avg(bom.spammer) as spammer
FROM `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u
JOIN `tweet-collector-py.impeachment_production.botometer_scores` bom ON bom.user_id = u.user_id -- 8683
WHERE bom.score_type IS NULL OR bom.score_type = 'english'
GROUP BY 1,2,3,4,5,6,7,8
--HAVING lookup_count > 1
--LIMIT 100

```

## Comparison

Get a list of our bot classifications, and the corresponding botometer scores, so we can compare them:

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

See [notebook](Botometer_Score_Comparisons.ipynb).
