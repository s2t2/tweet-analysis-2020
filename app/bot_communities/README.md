# Bot Communities

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

Assigning bots to spectral communities based on their similarity scores (using the same `BOT_MIN` from the previous step, and any small positive integer value for `K_COMMUNITIES`):

```sh
K_COMMUNITIES="2" BOT_MIN="0.8" python -m app.bot_communities.clustering
```

## Analysis

Downloading retweets / tweets for each bot community for local analysis (using the same `K_COMMUNITIES` and `BOT_MIN` from the previous step):

```sh
K_COMMUNITIES="2" BOT_MIN="0.8" python -m app.bot_communities.retweet_analyzer
```


```sh
K_COMMUNITIES="2" BOT_MIN="0.8" python -m app.bot_communities.tweet_analyzer
```

### Word Clouds

Downloading english stopwords (first time only):

```py
import nltk
nltk.download("stopwords")
```

```sh
K_COMMUNITIES="2" BOT_MIN="0.8" python -m app.bot_communities.retweet_wordclouds
```

Downloading spacy english language model (first time only):

```sh
python -m spacy download en_core_web_lg
```
