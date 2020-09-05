
import os

from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score #, classification_report

from sklearn.feature_extraction.text import TfidfVectorizer #, CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.pipeline import Pipeline
#from sklearn.model_selection import GridSearchCV

from app import DATA_DIR, seek_confirmation
from app.job import Job
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage, MODELS_DIRPATH

LIMIT = os.getenv("LIMIT") # just used to get smaller datasets for development purposes
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))

def get_training_data():
    bq_service = BigQueryService()
    job = Job()
    job.start()
    tweets = []
    for row in bq_service.fetch_labeled_tweets_in_batches(limit=LIMIT):
        tweets.append(dict(row))
        job.counter+=1
        if job.counter % BATCH_SIZE == 0:
            job.progress_report()
    job.end()
    #print("LABELED TWEETS:", fmt_n(len(tweets)))

    tweets_df = DataFrame(tweets)
    stratify = tweets_df["community_id"] # tweets_df[['community_id', 'date']]
    train_df, test_df = train_test_split(tweets_df, stratify=stratify, test_size=0.2, random_state=99)
    print("TEST/TRAIN SPLIT:", fmt_n(len(train_df)), fmt_n(len(test_df)))

    # TODO: THREE-WAY SPLIT (test/train/eval)

    return train_df, test_df

if __name__ == "__main__":

    train_df, test_df = get_training_data()
    training_text = train_df["status_text"]
    training_labels = train_df["community_id"]
    test_text = test_df["status_text"]
    test_labels = test_df["community_id"]

    print("--------------------------")
    print("TRAINING DATA...")
    print(fmt_n(len(train_df))) #> 800
    print(train_df.head())
    print(train_df["community_id"].value_counts()) # should be equal for each class!
    #raise ValueError("Expecting balanced training data") unless all counts are equal
    print("TESTING DATA...")
    print(test_df["community_id"].value_counts())

    print("--------------------------")
    print("VECTORIZING...")

    tv = TfidfVectorizer()
    tv.fit(training_text)
    print("FEATURES / TOKENS:", len(tv.get_feature_names())) #> 3842

    training_matrix = tv.transform(training_text)
    test_matrix = tv.transform(test_text)
    print("FEATURE MATRIX (TRAIN):", type(training_matrix), training_matrix.shape) # sparse (800, 3842)
    print("FEATURE MATRIX (TEST):", type(test_matrix), test_matrix.shape) # sparse (800, 3842)




    #
    # BINARY CLASSIFIERS
    #

    print("--------------------------")
    print("LOGISTIC REGRESSION...")

    clf = LogisticRegression(random_state=99)
    clf.fit(training_matrix, training_labels)

    training_predictions = clf.predict(training_matrix)
    training_score = accuracy_score(training_labels, training_predictions)
    print("ACCY (TRAIN):", training_score) #> 0.935

    test_predictions = clf.predict(test_matrix)
    test_score = accuracy_score(test_labels, test_predictions)
    print("ACCY (TEST):", test_score) #> 0.935

    print("SAVING/OVERWRITING (BEST) MODEL...")
    storage = ModelStorage(dirpath=os.path.join(MODELS_DIRPATH, "logistic_regression"))
    storage.save_vectorizer(tv)
    storage.save_model(clf)

    print("--------------------------")
    print("NAIVE BAYES (MULTINOMIAL)...")

    clf = MultinomialNB()
    clf.fit(training_matrix, training_labels)

    training_predictions = clf.predict(training_matrix)
    training_score = accuracy_score(training_labels, training_predictions)
    print("ACCY (TRAIN):", training_score) #> 0.92125

    test_predictions = clf.predict(test_matrix)
    test_score = accuracy_score(test_labels, test_predictions)
    print("ACCY (TEST):", test_score) #> 0.935

    print("SAVING/OVERWRITING (BEST) MODEL...")
    storage = ModelStorage(dirpath=os.path.join(MODELS_DIRPATH, "multinomial_nb"))
    storage.save_vectorizer(tv)
    storage.save_model(clf)
