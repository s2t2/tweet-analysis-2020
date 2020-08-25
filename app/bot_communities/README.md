# Bot Communities

## Setup

Downloading english stopwords (first time only):

```py
import nltk
nltk.download("stopwords")
```

Downloading spacy english language models (first time only):

```sh
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_md
python -m spacy download en_core_web_sm
```

## Prep

First, allow all daily classifications to complete and populate the "daily_bot_probabilities" table on BigQuery.

Constructing bot retweet graph, for all users who were assigned any daily bot scores above the given threshold (i.e. the `BOT_MIN`):

```sh
BOT_MIN="0.8" python -m app.bot_communities.bot_retweet_grapher
```

Constructing bot similarity graph (using the same `BOT_MIN` from the previous step):

```sh
BOT_MIN="0.8" python -m app.bot_communities.bot_similarity_grapher
```

## Assignment

Assigning bots to spectral communities based on their similarity scores (using the same `BOT_MIN` from the previous step, and any small positive integer value for `N_COMMUNITIES`):

```sh
BOT_MIN="0.8" N_COMMUNITIES="2" python -m app.bot_communities.spectral_clustermaker
```

> WARNING: this process will overwrite previous results, and due to randomness new results may not match.

## Analysis

Downloading retweets for each bot community for local analysis (using the same `N_COMMUNITIES` and `BOT_MIN` from the previous step):

```sh
BOT_MIN="0.8" N_COMMUNITIES="2" python -m app.bot_communities.retweet_analyzer
```

Downloading tweets for each bot community:

```sh
BOT_MIN="0.8" N_COMMUNITIES="2" python -m app.bot_communities.tweet_analyzer
```

### Daily Analysis

After downloading the local retweets.csv file, use it to generate daily wordclouds:

```sh
BOT_MIN="0.8" N_COMMUNITIES="2" APP_ENV="prodlike" MAX_THREADS=10 START_DATE="2020-01-01" END_DATE="2020-01-30" python -m app.bot_communities.daily_retweet_analyzer
```
