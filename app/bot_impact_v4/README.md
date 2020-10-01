# Assessing Bot Impact

## Daily Active User Friend Graphs

We are looking at all users who tweeted (at least X times) on a given day. We're assembling graphs for each of them and each of the people they follow who are also tweeting about impeachment (at some time, not necessarily on the same day):

```sh
#python -m app.bot_impact_v4.grapher
DATE="2020-01-23" TWEET_MIN=5 DESTRUCTIVE=true python -m app.bot_impact_v4.grapher
```
