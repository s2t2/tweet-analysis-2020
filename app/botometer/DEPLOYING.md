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
