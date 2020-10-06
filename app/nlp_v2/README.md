# NLP v2

## Data Labeling

Use the [existing labeled data](/app/nlp/README.md).

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
