
# Deploying (Retweet Graphs v2)

```sh
# repeat for servers 2-5:
heroku config:unset BATCH_SIZE                                -r heroku-2
heroku config:unset MAX_THREADS                               -r heroku-2
heroku config:unset MAX_USER_ID                               -r heroku-2
heroku config:unset MIN_USER_ID                               -r heroku-2
heroku config:unset USERS_LIMIT                               -r heroku-2
heroku config:unset JOB_ID                                    -r heroku-2
heroku config:unset STORAGE_MODE                              -r heroku-2
heroku config:unset DRY_RUN                                   -r heroku-2
heroku config:set K_DAYS="1"                                  -r heroku-2
heroku config:set GCS_BUCKET_NAME="impeachment-analysis-2020" -r heroku-2

# graphers (remaining periods not done on laptop):
heroku config:set START_DATE="2019-12-12"   -r heroku-2
heroku config:set N_PERIODS="17"            -r heroku-2

heroku config:set START_DATE="2020-02-15"   -r heroku-3
heroku config:set N_PERIODS="14"            -r heroku-3

heroku config:set START_DATE="2020-03-01"   -r heroku-4
heroku config:set N_PERIODS="20"            -r heroku-4

# classifiers (for periods already graphed on laptop):
heroku config:set START_DATE="2020-01-01"   -r heroku-5
heroku config:set N_PERIODS="3"             -r heroku-5
```

Deploying:

```sh
git push heroku-2 botz:master -f
git push heroku-3 botz:master -f
git push heroku-4 botz:master -f
git push heroku-5 botz:master -f
```

Then turn on the dynos, "Performance-M" tier might be ok, hopefully don't need "Performance-L".
