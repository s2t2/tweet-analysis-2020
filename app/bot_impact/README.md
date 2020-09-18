# Bot Impact Analysis

## Prep

```sh
START_DATE="2019-12-12" K_DAYS="1" N_PERIODS="75" python -m app.bot_impact.bq_prep.migrate_daily_friends_flat
```

## Usage

```sh
#APP_ENV="prodlike" DATE="2020-02-05" BATCH_SIZE="10000" python -m app.bot_impact.daily_friend_grapher
DATE="2020-02-05" APP_ENV=prodlike BATCH_SIZE=1000000 python -m app.bot_impact.daily_friend_grapher
```
