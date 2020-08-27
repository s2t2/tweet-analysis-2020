
# Follower Graphs

## Prerequisites

  + Ensure [friend collection](/app/friend_collection/README.md) has completed.
  + Ensure [bot classifications](/app/retweet_graphs_v2/README.md#K-Days-Bot-Classification) have been assigned.
  + Ensure [bot communities](/app/bot_communities/README.md/#Assignment) have been assigned.

## Usage

Generate graphs of bot follower network (using the same `BOT_MIN` from the bot classification step):

```sh
#BOT_MIN="0.8" BATCH_SIZE="500" python -m app.bot_follower_graphs.follower_grapher # not a good look
BOT_MIN="0.8" python -m app.bot_follower_graphs.follower_grapher_v2

BOT_MIN="0.8" python -m app.bot_follower_graphs.pg_follower_grapher_v2
```

Or download user friends table via PG pipeline and do it locally instead:

```sh
BOT_MIN="0.8" python -m app.bot_follower_graphs.follower_grapher_pg
```
