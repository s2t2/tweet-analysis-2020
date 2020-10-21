
# API Prep

Do manual things to get data for some of the charts.

## Daily Bot Probabilities Histogram

```sh
python -m api.prep.daily_bot_scores
```

Then copy the code "data/retweet_graphs_v2/k_days/1/2020-02-01/bot_probabilities_histogram.json" file into the react repo yeah!

TODO: loop through all days and upload them to single table in bigquery.
