# NLP v2

## Data Labeling

Follow all the same steps as before, operating on the same tables as before, but also add a step to de-dup the status texts to prevent over-fitting:

Since the same status text can be retweeted by many users and the resulting retweet text will be the same,
 we need to remove duplicate statuses from the training data, to prevent model over-fitting.

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

Then download a copy of that table into this directory as "data/nlp_v2/2_community_labeled_status_texts.csv".

Now you are ready for training.

## Model Training and Evaluation

Train some models on the labeled training data, and save them:

```py
APP_ENV="prodlike" python -m app.nlp_v2.model_training
```

## Model Predictions

Promote a given model to use for classification:

```sh
SOURCE="nlp_v2/models/2020-10-07-0220/logistic_regression" DESTINATION="nlp_v2/models/best/logistic_regression" python -m app.nlp_v2.model_promotion

SOURCE="nlp_v2/models/2020-10-07-0222/multinomial_nb" DESTINATION="nlp_v2/models/best/multinomial_nb" python -m app.nlp_v2.model_promotion
```

And use the trained model to make ad-hoc predictions:

```sh
python -m app.nlp_v2.client
```

Or to score all the unseen tweets:

```sh
APP_ENV="prodlike" LIMIT=10000 BATCH_SIZE=900 python -m app.nlp_v2.bulk_predict
```
