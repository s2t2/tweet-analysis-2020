# Deploying


> FYI: You have to use API Keys from different basilica accounts on each server or else you'll hit lots of Bad Gateway errors... JK it still runs into errors. Have to turn max threads down to 1... JK it still happens even at one thread. Basilica killing me...

Configure env vars on the server:

```sh
heroku config:set BASILICA_API_KEY="_______________" -r heroku-2
heroku config:set BASILICA_API_KEY="_______________" -r heroku-3
heroku config:set BASILICA_API_KEY="_______________" -r heroku-4
heroku config:set BASILICA_API_KEY="_______________" -r heroku-5

heroku config:set MIN_VAL="0.1" -r heroku-2
heroku config:set MIN_VAL="0.2" -r heroku-3
heroku config:set MIN_VAL="0.3" -r heroku-4
heroku config:set MIN_VAL="0.4" -r heroku-5

heroku config:set MAX_VAL="0.2" -r heroku-2
heroku config:set MAX_VAL="0.3" -r heroku-3
heroku config:set MAX_VAL="0.4" -r heroku-4
heroku config:set MAX_VAL="0.5" -r heroku-5

heroku config:set LIMIT=50000 -r heroku-2
heroku config:set LIMIT=50000 -r heroku-3
heroku config:set LIMIT=50000 -r heroku-4
heroku config:set LIMIT=50000 -r heroku-5

heroku config:set BATCH_SIZE=500 -r heroku-2
heroku config:set BATCH_SIZE=500 -r heroku-3
heroku config:set BATCH_SIZE=500 -r heroku-4
heroku config:set BATCH_SIZE=500 -r heroku-5

heroku config:set MAX_THREADS=1 -r heroku-2
heroku config:set MAX_THREADS=1 -r heroku-3
heroku config:set MAX_THREADS=1 -r heroku-4
heroku config:set MAX_THREADS=1 -r heroku-5
```

Deploy:

```sh
git push heroku-2 embedz:master -f
git push heroku-3 embedz:master -f
git push heroku-4 embedz:master -f
git push heroku-5 embedz:master -f
```

Then turn on the "basilica_embedder" dyno on all servers and monitor the logs.
