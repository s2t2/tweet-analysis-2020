# Notes

## Data Labeling

Since the same status text can be retweeted by many users and the resulting retweet text will be the same,
 we need to remove duplicate statuses from the training data, to prevent model over-fitting.

Originally we were thinking just de-dup the statuses, but when a status is repeated and is retweeted by members of the same community, we could perhaps drop the status, but why don't we take the mean community score, to give the status a more accurate label than just the normal 0 or 1 from earlier. So let's roll with this...

```sql
CREATE TABLE impeachment_production.2_community_labeled_status_texts as (
  SELECT
    status_text
    ,count(distinct status_id) as status_occurrences
    ,avg(community_id) as avg_community_score
    -- TODO maybe add the median or mode community score as well
  FROM impeachment_production.2_community_labeled_tweets
  GROUP BY 1
  -- HAVING status_occurrences > 1 and avg_community_score between 0.3 and 0.7
  -- ORDER BY 2 DESC
) -- 2,771,905 tweets
```

## Predictions

Check the uploaded predictions and make a backup in case we accidentally overwrite them in the future:

```sql
/*
SELECT status_id, prediction
FROM impeachment_production.nlp_v2_predictions_logistic_regression lr
LIMIT 10
*/

/*
SELECT count(distinct status_id) as status_count
--FROM impeachment_production.nlp_v2_predictions_logistic_regression lr -- 67,636,557
-- FROM impeachment_production.nlp_v2_predictions_multinomial_nb nb -- 67,666,557
*/

CREATE TABLE impeachment_production.nlp_v2_predictions_logistic_regression_backup as (
  SELECT status_id, prediction
  FROM impeachment_production.nlp_v2_predictions_logistic_regression
)

CREATE TABLE impeachment_production.nlp_v2_predictions_multinomial_nb_backup as (
  SELECT status_id, prediction
  FROM impeachment_production.nlp_v2_predictions_multinomial_nb
)
```

## Analysis

```sql
DROP TABLE IF EXISTS impeachment_production.nlp_v2_predictions_combined;
CREATE TABLE impeachment_production.nlp_v2_predictions_combined as (
  SELECT DISTINCT
    cast(t.user_id as int64) as user_id
    ,upper(t.user_screen_name) as screen_name
    ,t.user_created_at

    ,t.status_id
    ,t.created_at
    ,t.status_text
    ,lr.prediction as prediction_lr
    ,nb.prediction as prediction_nb
    ,NULL as prediction_bert

    ,case when lr.prediction = "D" then 0 when lr.prediction = "R" then 1 end score_lr
    ,case when nb.prediction = "D" then 0 when nb.prediction = "R" then 1 end score_nb
    ,NULL as score_bert

  FROM impeachment_production.tweets t
  LEFT JOIN impeachment_production.nlp_v2_predictions_logistic_regression lr ON lr.status_id = cast(t.status_id as int64)
  LEFT JOIN impeachment_production.nlp_v2_predictions_multinomial_nb nb ON nb.status_id = cast(t.status_id as int64)
)
```


Also user aggregated table(s):

```sql
DROP TABLE IF EXISTS impeachment_production.nlp_v2_predictions_by_user;
CREATE TABLE impeachment_production.nlp_v2_predictions_by_user as (
  SELECT
    p.user_id
    ,p.screen_name
    ,p.user_created_at
    ,count(distinct p.status_id) as status_count
    ,max(sn.follower_id_count) as follower_count

    ,avg(p.score_lr) avg_score_lr
    ,avg(p.score_nb) avg_score_nb

  FROM impeachment_production.nlp_v2_predictions_combined p
  LEFT JOIN impeachment_production.user_screen_names_most_followed sn ON upper(p.screen_name) = upper(sn.user_screen_name)
  GROUP BY 1,2,3
  ORDER BY 5 DESC
  -- LIMIT 200
)
```

Top 100,000 users most followed:

```sql
DROP TABLE IF EXISTS impeachment_production.nlp_v2_predictions_by_user_most_followed;
CREATE TABLE impeachment_production.nlp_v2_predictions_by_user_most_followed as (
  SELECT
    user_id
    ,screen_name
    ,user_created_at
    ,status_count
    ,follower_count

    ,avg_score_lr
    ,avg_score_nb

  FROM nlp_v2_predictions_by_user
  WHERE status_count >= 3
  ORDER BY follower_count DESC
  LIMIT 1000
)
```

Then connect to this table from Tableau and check out the distributions and the average scores for each user.

What about distribution of mean score for all users?

```sql
CREATE TABLE impeachment_production.nlp_v2_user_scores_binned_lr as (
  SELECT
    avg_lr_bin
    ,count(distinct user_id) as user_count
  FROM (
    SELECT
      t.user_id
      ,upper(t.user_screen_name) as screen_name
      ,count(distinct t.status_id) as status_count

      ,avg(score_lr) as avg_lr
      ,avg(score_nb) as avg_nb
      ,round(avg(score_lr) * 100) / 100 as avg_lr_bin
      ,round(avg(score_nb) * 100) / 100 as avg_nb_bin

    FROM impeachment_production.nlp_v2_predictions_combined p
    JOIN impeachment_production.tweets t ON cast(t.status_id as int64) = cast(p.status_id as int64)
    -- WHERE screen_name = 'POLITICO'
    GROUP BY 1,2
    -- LIMIT 100
  )
  GROUP BY 1
)


CREATE TABLE impeachment_production.nlp_v2_user_scores_binned_nb as (
  SELECT
    avg_nb_bin
    ,count(distinct user_id) as user_count
  FROM (
    SELECT
      t.user_id
      ,upper(t.user_screen_name) as screen_name
      ,count(distinct t.status_id) as status_count

      ,avg(score_lr) as avg_lr
      ,avg(score_nb) as avg_nb
      ,round(avg(score_lr) * 100) / 100 as avg_lr_bin
      ,round(avg(score_nb) * 100) / 100 as avg_nb_bin

    FROM impeachment_production.nlp_v2_predictions_combined p
    JOIN impeachment_production.tweets t ON cast(t.status_id as int64) = cast(p.status_id as int64)
    -- WHERE screen_name = 'POLITICO'
    GROUP BY 1,2
    -- LIMIT 100
  )
  GROUP BY 1
)

```
