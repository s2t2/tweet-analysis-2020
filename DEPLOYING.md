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


heroku config:set BIGQUERY_DATASET_NAME="impeachment_production"
heroku config:set MIN_USER_ID="17"
heroku config:set MAX_USER_ID="49223966"
heroku config:set USERS_LIMIT="10000"
heroku config:set BATCH_SIZE="20"
heroku config:set MAX_THREADS="20"
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
heroku run "python -m app.storage_service"
```

Run the collection script in production, manually:

```sh
heroku run "python -m app.friend_collector"
```

... though ultimately you'll want to setup a Heroku "dyno" (hobby tier) to run the collection script as a background process (see the "Procfile"):

```sh
heroku run friend_collector
```

Checking logs:

```sh
heroku logs --ps friend_collector
```
