# Bot Impact Analysis

## Usage

```sh
APP_ENV="prodlike" DATE="2020-02-05" BATCH_SIZE="1000" python -m app.bot_impact.daily_friend_grapher
```

These are too big to create, so how about some smaller, topic-specific friend graphs?

```sh
APP_ENV=prodlike DATE="2020-02-05" BATCH_SIZE="100" python -m app.bot_impact.daily_community_friend_grapher
```

No, instead let's keep only users who tweeted more than 3 times that day:

```sh
APP_ENV=prodlike DATE="2020-02-05" BATCH_SIZE="1000" python -m app.bot_impact.daily_friend_grapher_for_active_tweeters
```
