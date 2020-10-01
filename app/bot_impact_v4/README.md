# Assessing Bot Impact

## Daily Active User Friend Graphs

We are looking at all users who tweeted (at least X times) on a given day. We're assembling graphs for each of them and each of the people they follow who are also tweeting about impeachment (at some time, or on that same day, respectively):

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_user_friend_grapher
```

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_edge_friend_grapher
```
