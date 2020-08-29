
# Follower Graphs

## Prerequisites

  + Ensure [friend collection](/app/friend_collection/README.md) has completed.
  + Ensure [bot classifications](/app/retweet_graphs_v2/README.md#K-Days-Bot-Classification) have been assigned, and use the same `BOT_MIN` below.

## Setup

First migrate the respective BigQuery tables ("user_friends_flat", "bots_over_80", "bot_followers_over_80"):

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.bq_prep
```

## Usage

Use either the BQ or PG version. They perform at a rate of around a minute per thousand bots. So if you have 25K bots, it will only take a half hour.

### BQ Grapher

Generate graphs of bot follower network (using the same `BOT_MIN` from the bot classification step):

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.bq_grapher
```

### PG Grapher

After migrating BQ tables, download only the "bot_followers_over_80" table:

```sh
BOT_MIN="0.8" python -m app.pg_pipeline.bot_followers
```

Generate graphs of bot follower network (using the same `BOT_MIN` from the bot classification step):

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.pg_grapher
```
