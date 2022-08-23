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
SELECT

    count(distinct bom.user_id) as users_with_lookups
    ,count(distinct CASE WHEN bom.error_message IS NOT NULL THEN bom.user_id END) users_with_errors
    ,count(distinct CASE WHEN bom.error_message IS NULL THEN bom.user_id END) users_with_scores
    ,count(distinct CASE WHEN bom.error_message IS NULL AND u.is_bot=TRUE THEN bom.user_id END) bots_with_scores
    ,count(distinct CASE WHEN bom.error_message IS NULL AND u.is_bot=FALSE THEN bom.user_id END) humans_with_scores

    ,avg(cap) as avg_cap
    ,avg(CASE WHEN u.is_bot=TRUE THEN cap END) as avg_cap_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN cap END) as avg_cap_humans

    ,avg(astroturf) as avg_astroturf
    ,avg(CASE WHEN u.is_bot=TRUE THEN astroturf END) as avg_astroturf_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN astroturf END) as avg_astroturf_humans

    ,avg(fake_follower) as avg_fake_follower
    ,avg(CASE WHEN u.is_bot=TRUE THEN fake_follower END) as avg_fake_follower_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN fake_follower END) as avg_fake_follower_humans

    ,avg(financial) as avg_financial
    ,avg(CASE WHEN u.is_bot=TRUE THEN financial END) as avg_financial_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN financial END) as avg_financial_humans

    ,avg(other) as avg_other
    ,avg(CASE WHEN u.is_bot=TRUE THEN other END) as avg_other_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN other END) as avg_other_humans

    ,avg(overall) as avg_overall
    ,avg(CASE WHEN u.is_bot=TRUE THEN overall END) as avg_overall_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN overall END) as avg_overall_humans

    ,avg(self_declared) as avg_declared
    ,avg(CASE WHEN u.is_bot=TRUE THEN self_declared END) as avg_declared_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN self_declared END) as avg_declared_humans

    ,avg(spammer) as avg_spammer
    ,avg(CASE WHEN u.is_bot=TRUE THEN spammer END) as avg_spammer_bots
    ,avg(CASE WHEN u.is_bot=FALSE THEN spammer END) as avg_spammer_humans


FROM `tweet-collector-py.impeachment_production.botometer_scores` bom
JOIN `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u ON u.user_id = bom.user_id

```
