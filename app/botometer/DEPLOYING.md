# Deploying


Whoah it's been a while. What servers do we have? OK let's choose one (-r heroku-9  / -a impeachment-tweet-analysis-9).

## Configuration

Reconfig vars:

```sh
heroku config:set RAPID_API_KEY="___________"  -r heroku-9
heroku config:set LIMIT=1500  -r heroku-9

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
