
# Natural Language Processing (NLP)

## Tweet Labeling

Identify a list of around ten hashtags used by members of each of N communities (i.e. two), and store this information in a CSV file:

```csv
community_id,hashtag,description
0, #LEFTTAG,
0, #LEFTTAG2,
1, #RIGHTTAG, It means this
1, #RIGHTTAG2
```

> Ideally these hashtags are mutually exclusive (used by one community and not any others), or have minimal overlap. Users whose profiles include hashtags from more than one community will be excluded from the training data.

Upload this CSV file to BigQuery as the "2_community_tags" table.

### Migrations

A table of user information, with all their names and descriptions represented as a single pipe-concatenated string:

```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v3;
CREATE TABLE impeachment_production.user_details_v3 as (
    SELECT
        cast(t.user_id as int64) as user_id
        ,min(t.user_created_at) as user_created_at
        ,count(distinct t.status_id) as tweet_count
        ,count(distinct t.user_screen_name) as screen_name_count
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_screen_name), ' | ') , "")   as screen_names
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_name), ' | ')        , "")   as user_names
        ,COALESCE(STRING_AGG(DISTINCT upper(t.user_description), ' | ') , "")   as user_descriptions
    FROM impeachment_production.tweets t
    GROUP BY 1
)
```

Determine which users have included any of the given hashtags in their profile descriptions:

```sql
DROP TABLE IF EXISTS impeachment_production.user_community_scores;
CREATE TABLE impeachment_production.user_community_scores as (
  SELECT
    user_id -- ,user_names ,user_descriptions
    ,community_id
    ,count(distinct hashtag) as community_score
  FROM (
    SELECT
          user_id -- , screen_names , user_names, user_descriptions
          ,split(user_names, ' ') as name_tokens
          ,split(user_descriptions, ' ') as description_tokens
    FROM impeachment_production.user_details_v3
    -- LIMIT 10
  ) tk
  JOIN impeachment_production.2_community_tags tg ON tg.hashtag in UNNEST(tk.description_tokens) -- or tg.hashtag in unnest(tk.name_tokens))
  GROUP BY 1,2
  ORDER BY 1
  --LIMIT 10
);
```

Assign each user a community label and score, and exclude users who have tags from more than one community:

```sql
DROP TABLE IF EXISTS impeachment_production.user_2_community_assignments;
CREATE TABLE impeachment_production.user_2_community_assignments as (
  -- users who are in only one community
  SELECT
    ucs.user_id, ucs.community_id , ucs.community_score
  FROM impeachment_production.user_community_scores ucs
  JOIN (
    SELECT user_id
    FROM impeachment_production.user_community_scores
    GROUP BY 1
    HAVING count(distinct community_id) = 1 -- 137,460
  ) polar_users ON polar_users.user_id = ucs.user_id
)
```

Finally apply these user community labels to their tweets:

```sql
DROP TABLE IF EXISTS impeachment_production.2_community_labeled_tweets;
CREATE TABLE impeachment_production.2_community_labeled_tweets as (
  SELECT
    ul.user_id
    ,ul.community_id
    ,ul.community_score
    ,t.status_id
    ,t.status_text
    ,t.created_at
  FROM impeachment_production.user_2_community_assignments ul
  JOIN impeachment_production.tweets t ON cast(t.user_id as int64) = ul.user_id
);
```

We'll use these labeled tweets as the training data.

## Usage

Test the model storage service:

```sh
python -m app.nlp.model_storage
```

Train some models on the labeled training data:

```py
# LIMIT=10000 BATCH_SIZE=1000 python -m app.nlp.model_training

APP_ENV="prodlike" BATCH_SIZE=25000 python -m app.nlp.model_training
```

Promote a given model to use for classifications:

```sh
MODEL_DIRPATH="tweet_classifier/models/logistic_regression/2020-09-09-1719" python -m app.nlp.model_promotion python -m app.nlp.model_promotion
```

And use the trained model to make ad-hoc predictions:

```sh
python -m app.nlp.client
```

Or to score all the unseen tweets:

```sh
# LIMIT=10000 BATCH_SIZE=1000 python -m app.nlp.bulk_predict
APP_ENV="prodlike" python -m app.nlp.bulk_predict
```
