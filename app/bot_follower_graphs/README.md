
# Follower Graphs

## Prerequisites

  + Ensure [friend collection](/app/friend_collection/README.md) has completed.
  + Ensure [bot classifications](/app/retweet_graphs_v2/README.md#K-Days-Bot-Classification) have been assigned.
  + Ensure [bot communities](/app/bot_communities/README.md/#Assignment) have been assigned.

## Usage

Generate daily graphs of bot follower networks (using the same `N_COMMUNITIES` and `BOT_MIN` from the bot community assignment step):

```sh
BOT_MIN="0.8" N_COMMUNITIES="2" K_DAYS="1" START_DATE="2019-12-12" N_PERIODS="60" python -m app.bot_follower_graphs.k_days.grapher
```
