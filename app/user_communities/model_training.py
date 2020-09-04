
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

from app import DATA_DIR
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService

LIMIT = os.getenv("LIMIT") # just used to get smaller datasets for development purposes

def get_training_data():
    bq_service = BigQueryService()

    print("--------------------------")
    tweets = []
    for row in bq_service.fetch_labeled_tweets_in_batches(limit=LIMIT):
        tweets.append(dict(row))
    print("LABELED TWEETS:", fmt_n(len(tweets)))

    tweets_df = DataFrame(tweets)
    stratify = tweets_df["community_id"] # population[['income', 'sex', 'age']]
    train_df, test_df = train_test_split(tweets_df, stratify=stratify, test_size=0.2, random_state=99)
    print("TEST/TRAIN SPLIT:", fmt_n(len(train_df)), fmt_n(len(test_df)))

    # TODO: test/train/ eval split
    return train_df #, test_df

if __name__ == "__main__":

    print("--------------------------")
    print("TRAINING DATA...")

    train_df = get_training_data()
    print(len(train_df)) #> 800
    print(train_df.head())
    print(train_df["community_id"].value_counts()) # should be equal for each class!
    #raise ValueError("Expecting balanced training data") unless all counts are equal

    training_text = train_df["status_text"]
    training_labels = train_df["community_id"]

    print("--------------------------")
    print("VECTORIZING (TF/IDF)...")

    tv = TfidfVectorizer()
    tv.fit(training_text)
    print("FEATURES / TOKENS:", len(tv.get_feature_names())) #> 3842

    training_matrix = tv.transform(training_text)
    print("FEATURE MATRIX:", type(training_matrix), training_matrix.shape) # sparse (800, 3842)

    #
    # BINARY CLASSIFIERS
    #

    print("--------------------------")
    print("LOGISTIC REGRESSION...")

    clf = LogisticRegression(random_state=99)
    clf.fit(training_matrix, training_labels)

    training_predictions = clf.predict(training_matrix)
    training_score = accuracy_score(training_labels, training_predictions)
    print("ACCY:", training_score) #> 0.935

    print("--------------------------")
    print("NAIVE BAYES (MULTINOMIAL)...")

    clf = MultinomialNB()
    clf.fit(training_matrix, training_labels)

    training_predictions = clf.predict(training_matrix)
    training_score = accuracy_score(training_labels, training_predictions)
    print("ACCY:", training_score) #> 0.92125
