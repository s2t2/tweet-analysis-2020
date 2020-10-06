# NLP v2

## Data Labeling

Follow all the same steps as before, operating on the same tables as before, but also add a step to de-dup the status texts to prevent over-fitting:

```sql
-- TODO SEE NOTES.md
```

Then download a copy of that table into this directory as "data/nlp_v2/2_community_labeled_status_texts.csv".

Now you are ready for training.

## Model Training and Evaluation

Train some models on the labeled training data:

```py
python -m app.nlp_v2.model_training
```

## Model Predictions

Promote a given model to use for classifications:

```sh
MODEL_DIRPATH="tweet_classifier/models/logistic_regression/2020-09-09-1719" python -m app.nlp.model_promotion python -m app.nlp_v2.model_promotion
```

And use the trained model to make ad-hoc predictions:

```sh
python -m app.nlp_v2.client
```

Or to score all the unseen tweets:

```sh
APP_ENV="prodlike" python -m app.nlp_v2.bulk_predict
```
