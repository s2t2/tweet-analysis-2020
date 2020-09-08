
import os
from datetime import datetime
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score #, classification_report

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.pipeline import Pipeline
#from sklearn.model_selection import GridSearchCV

from app import APP_ENV, DATA_DIR, seek_confirmation
from app.job import Job
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage, MODELS_DIRPATH

LIMIT = os.getenv("LIMIT") # just used to get smaller datasets for development purposes
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))

def get_tweets():
    bq_service = BigQueryService()
    print("LIMIT:", LIMIT)
    job = Job()

    tweets = []
    job.start()
    for row in bq_service.fetch_labeled_tweets_in_batches(limit=LIMIT):
        tweets.append(dict(row))
        job.counter+=1
        if job.counter % BATCH_SIZE == 0:
            job.progress_report()
    job.end()
    print("FETCHED TWEETS:", fmt_n(len(tweets)))
    return DataFrame(tweets)

if __name__ == "__main__":

    tweets_df = get_tweets()

    train_df, test_df = train_test_split(tweets_df, stratify=tweets_df["community_id"], test_size=0.2, random_state=99)
    print("TEST/TRAIN SPLIT:", fmt_n(len(train_df)), fmt_n(len(test_df))) # consider: THREE-WAY SPLIT (test/train/eval)

    print("--------------------------")
    print("TRAINING DATA...")
    print(fmt_n(len(train_df))) #> 800
    print(train_df.head())
    print(train_df["community_id"].value_counts()) # should be equal for each class!
    #raise ValueError("Expecting balanced training data") unless all counts are equal
    training_text = train_df["status_text"]
    training_labels = train_df["community_id"]

    print("--------------------------")
    print("TESTING DATA...")
    print(fmt_n(len(train_df))) #> 200
    print(test_df["community_id"].value_counts())
    test_text = test_df["status_text"]
    test_labels = test_df["community_id"]

    print("--------------------------")
    print("VECTORIZING...")

    tv = TfidfVectorizer()
    tv.fit(training_text)
    print("FEATURES / TOKENS:", fmt_n(len(tv.get_feature_names()))) #> 3842

    training_matrix = tv.transform(training_text)
    print("FEATURE MATRIX (TRAIN):", type(training_matrix), training_matrix.shape) # sparse (800, 3842)

    test_matrix = tv.transform(test_text)
    print("FEATURE MATRIX (TEST):", type(test_matrix), test_matrix.shape) # sparse (800, 3842)

    #
    # MODELS (CUSTOM PIPELINE)
    #

    models = {
        "logistic_regression": LogisticRegression(random_state=99),
        "multinomial_nb": MultinomialNB()
    }

    #for model_name, model in models.values(): # TypeError: cannot unpack non-iterable LogisticRegression object
    for model_name in models.keys():
        model = models[model_name]
        print("--------------------------")
        print(f"{model_name.upper()}...")
        print(model)

        model.fit(training_matrix, training_labels)

        training_predictions = model.predict(training_matrix)
        training_score = accuracy_score(training_labels, training_predictions)
        print("ACCY SCORE (TRAIN):", training_score) #> 0.935

        test_predictions = model.predict(test_matrix)
        test_score = accuracy_score(test_labels, test_predictions)
        print("ACCY SCORE (TEST):", test_score) #> 0.935

        print("SAVING...")
        if APP_ENV == "development":
            model_id = "dev"
        else:
            model_id = datetime.now().strftime("%Y-%m-%d-%H%M")
        storage = ModelStorage(dirpath=f"{MODELS_DIRPATH}/{model_name}/{model_id}")
        storage.save_vectorizer(tv)
        storage.save_model(model)
        storage.save_scores({
            "features": len(tv.get_feature_names()),
            "training_matrix": training_matrix.shape,
            "training_accy": training_score,
            "test_matrix": test_matrix.shape,
            "test_accy": test_score
        })
