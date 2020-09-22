# Bot Impact Analysis

## Usage

```sh
APP_ENV="prodlike" DATE="2020-02-05" BATCH_SIZE="1000" python -m app.bot_impact.daily_friend_grapher
```

These are too big to create, so instead let's keep only users who tweeted more than `TWEET_MIN` times that day:

```sh
APP_ENV=prodlike DATE="2020-02-05" TWEET_MIN=5 BATCH_SIZE="1000" python -m app.bot_impact.daily_active_user_friend_grapher
```
