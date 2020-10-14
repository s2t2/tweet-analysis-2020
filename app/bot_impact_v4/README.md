# Assessing Bot Impact

## Daily Active User Friend Graphs

We are looking at all users who tweeted (at least X times) on a given day. We're assembling graphs for each of them and each of the people they follow who are also tweeting about impeachment (at some time, or on that same day, respectively):

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_user_friend_grapher
```

```sh
DATE="2020-01-23" TWEET_MIN=5 python -m app.bot_impact_v4.daily_active_edge_friend_grapher
```

## For Real Though (v5)


JK JK, we're going to dynamically find the tweet min, and we also want to include tweet opinion scores:

```sh
START_DATE="2019-12-20" N_PERIODS=60 python -m app.bot_impact_v4.daily_active_edge_downloader

APP_ENV="prodlike" START_DATE="2020-01-08" N_PERIODS=40 python -m app.bot_impact_v4.daily_active_edge_downloader
```

This produces daily "nodes.csv" and "tweets.csv" files in the "daily_active_edge_friend_graphs_v5". Upload these CSV files to Google Drive, where we are running the impact assessment notebook w/ BERT classifier for each day. TODO: auto-upload to Google Drive.
