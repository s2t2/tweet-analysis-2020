# Retweet Graphs v3

After collecting tweets, our goal is to detect similarities in retweet activity between users.

## Setup

### BQ Setup

First, create a new dataset called "election_2020_analysis" or something, and set the `BIGQUERY_DATASET_NAME` env var accordingly.

Copy tweets there:

```sql
DROP TABLE IF EXISTS election_2020_analysis.tweets;
CREATE TABLE election_2020_analysis.tweets as (
    SELECT DISTINCT
        cast(status_id as int64) as status_id
        ,status_text
        ,truncated
        ,cast(retweeted_status_id as int64) as retweeted_status_id
        ,cast(retweeted_user_id as int64) as retweeted_user_id
        ,upper(retweeted_user_screen_name) as retweeted_user_screen_name
        ,cast(reply_status_id as int64) as reply_status_id
        ,cast(reply_user_id as int64) as reply_user_id
        ,is_quote
        ,geo
        ,created_at
        ,cast(user_id as int64) as user_id
        ,user_name
        ,upper(user_screen_name) as user_screen_name
        ,user_description
        ,user_location
        ,user_verified
        ,user_created_at
    FROM election_2020_production.tweets
-- LIMIT 10
);
```

### GCS Setup

Create a new bucket called "election-analysis-2020" and set the `GCS_BUCKET_NAME` env var accordingly.

## Usage

### Constructing Retweet Graphs

```sh
START_DATE="2020-09-26" END_DATE="2020-10-03" python -m app.retweet_graphs_v3.retweet_grapher
```

### Classifying Bots

```sh
START_DATE="2020-09-26" END_DATE="2020-10-03" python -m app.retweet_graphs_v3.bot_classifier
```

Then import the CSV file from GCS or CSV into BQ, into a table called "bot_probabilities".
