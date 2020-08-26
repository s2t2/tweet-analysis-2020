
# Follower Graphs

## Prerequisites

  + Ensure [friend collection](/app/friend_collection/README.md) has completed.
  + Ensure [bot classifications](/app/retweet_graphs_v2/README.md#K-Days-Bot-Classification) have been assigned.
  + Ensure [bot communities](/app/bot_communities/README.md/#Assignment) have been assigned.

## Usage

Generate graphs of bot follower network (using the same `N_COMMUNITIES` and `BOT_MIN` from the bot community assignment step):

```sh
BOT_MIN="0.8" BATCH_SIZE="500" python -m app.bot_follower_graphs.follower_grapher
```
