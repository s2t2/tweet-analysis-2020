import os

from app.nlp.model_storage import ModelStorage

MODEL_DIRPATH = os.getenv("MODEL_DIRPATH", default="tweet_classifier/models/logistic_regression/2020-09-08-1229")


if __name__ == "__main__":

    storage = ModelStorage(dirpath=MODEL_DIRPATH)

    storage.promote_model()
