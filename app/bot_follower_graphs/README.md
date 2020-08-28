
# Follower Graphs

## Prerequisites

  + Ensure [friend collection](/app/friend_collection/README.md) has completed.
  + Ensure [bot classifications](/app/retweet_graphs_v2/README.md#K-Days-Bot-Classification) have been assigned.
  + Ensure [bot communities](/app/bot_communities/README.md/#Assignment) have been assigned.


## Usage

### BQ Grapher

Generate graphs of bot follower network (using the same `BOT_MIN` from the bot classification step):

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.bq_grapher
```

### PG Grapher

First download "bot_followers_over_80" table via PG pipeline:

```sh
BOT_MIN="0.8" python -m app.pg_pipeline_v2.download_bot_followers
```

Generate graphs of bot follower network (using the same `BOT_MIN` from the bot classification step):

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.pg_grapher
```
