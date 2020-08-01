# Deploying to Heroku

Create a new app server (first time only):

```sh
heroku create impeachment-tweet-analysis # (use your own app name here)
```

Provision and configure the Google Application Credentials Buildpack to generate a credentials file on the server:

```sh
heroku buildpacks:set heroku/python
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack
heroku config:set GOOGLE_CREDENTIALS="$(< credentials.json)" # references local creds
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json"
```

Configure the rest of the environment variables (see [Partitioning Users](/NOTES.md#partitioning-users)):

```sh
heroku config:set APP_ENV="production"
heroku config:set SERVER_NAME="impeachment-tweet-analysis-10" # or whatever yours is called

heroku config:set BIGQUERY_DATASET_NAME="impeachment_production"
heroku config:set MIN_USER_ID="17"
heroku config:set MAX_USER_ID="49223966"
heroku config:set USERS_LIMIT="10000"
heroku config:set BATCH_SIZE="20"
heroku config:set MAX_THREADS="20"

heroku config:set SENDGRID_API_KEY="_____________"
heroku config:set MY_EMAIL_ADDRESS="me@example.com"

heroku config:set GCS_BUCKET_NAME="impeachment-analysis-2020" -r heroku-4

```

Deploy:

```sh
# from master branch
git checkout master
git push heroku master

# or from another branch
git checkout mybranch
git push heroku mybranch:master
```

Test everything is working in production:

```sh
heroku run "python -m app.bq_service"
```

You could run the friend collection script in production, manually:

```sh
heroku run "python -m app.friend_collection.batch_per_thread"
```

... though ultimately you'll want to setup a Heroku "dyno" (hobby tier) to run the friend collection script as a background process (see the "Procfile"):

```sh
heroku run friend_collector
```

Checking logs:

```sh
heroku logs --ps friend_collector
```

Running network grapher:

```sh
heroku config:set BATCH_SIZE=1000 -r heroku-4
heroku config:set BIGQUERY_DATASET_NAME="impeachment_production" -r heroku-4
heroku config:set DRY_RUN="false" -r heroku-4
heroku run:detached "python -m app.friend_graphs.bq_grapher" -r heroku-4
```

Running graph analyzer:

```sh
heroku config:set STORAGE_MODE="remote" -r heroku-4

heroku config:set JOB_ID="2020-05-30-0338" -r heroku-4 # FIRST
heroku config:set JOB_ID="2020-06-07-2049" -r heroku-4 # RIGHT
heroku config:set JOB_ID="2020-06-07-2056" -r heroku-4 # LEFT

#heroku run:detached "python -m app.graph_analyzer" -r heroku-4
heroku run graph_analyzer -r heroku-4
```
