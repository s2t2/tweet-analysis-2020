# Deployment Instructions

Ensure Procfile contains:

```
web: gunicorn "api:create_app()"
```

Create a new server:

```sh
heroku create -n impeachment-tweet-analysis-api
git remote add heroku-api https://git.heroku.com/impeachment-tweet-analysis-api.git

heroku buildpacks:set heroku/python -r heroku-api
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack -r heroku-api
```

Configure the server:

```sh
heroku config:set GOOGLE_CREDENTIALS="$(< credentials.json)" -r heroku-api
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json" -r heroku-api

heroku config:set APP_ENV="production" -r heroku-api
heroku config:set SERVER_NAME="impeachment-tweet-analysis-api" -r heroku-api
heroku config:set BIGQUERY_DATASET_NAME="impeachment_production" -r heroku-api
```

Deploy:


```sh
git push heroku-api api-v0:master
```
