
import os
from datetime import datetime
from pprint import pprint

from pandas import DataFrame, read_csv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report # accuracy_score

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

def load_labeled_status_texts():
    filepath = os.path.join(DATA_DIR, "nlp_v2", "2_community_labeled_status_texts.csv")
    if os.path.isfile(filepath):
        return read_csv(filepath)
    else:
        return fetch_tweets()

def fetch_labeled_status_texts():
    print("FETCHING LABELED STATUSES FOR TRAINING")
    #bq_service = BigQueryService()
    #print("LIMIT:", LIMIT)
    #job = Job()
    #records = []
    #job.start()
    #for row in bq_service.fetch_labeled_status_texts(limit=LIMIT):
    #    records.append(dict(row))
    #    job.counter+=1
    #    if job.counter % BATCH_SIZE == 0:
    #        job.progress_report()
    #job.end()
    #print("FETCHED STATUSES:", fmt_n(len(records)))
    #return DataFrame(records)

def bin_the_middle(val):
    if 0 < val and val < 1:
        val = 0.5
    return val

def generate_histogram(df, column_name):
    #print("ROWS:", fmt_n(len(df)))
    #print(df.head())
    #print("VALUE COUNTS:")
    print(df[column_name].value_counts())


if __name__ == "__main__":

    text_column = "status_text"
    label_column = "community_label"

    print("--------------------------")
    print("LOADING LABELED DATA...")
    df = load_labeled_status_texts()
    generate_histogram(df, "avg_community_score")

    print("--------------------------")
    print("BINNING MIDDLE VALUES...")
    # If you leave some of the 1 count labels in, when you try to stratify, you'll get ValueError: The least populated class in y has only 1 member, which is too few. The minimum number of groups for any class cannot be less than 2.
    # So let's take all the statuses with a score in-between 0 and 1, and give them a label of 0.5 (not sure)
    df[label_column] = df["avg_community_score"].apply(bin_the_middle)
    df.drop(["avg_community_score", "status_occurrences"], axis="columns", inplace=True)
    generate_histogram(df, label_column)

    print("--------------------------")
    print("SPLITTING...")
    training_df, test_df = train_test_split(df, stratify=df[label_column], test_size=0.2, random_state=99)

    print("--------------------------")
    print("TRAINING DATA SUMMARY:")
    generate_histogram(training_df, label_column) # should ideally be around equal for each class!
    training_text = training_df[text_column]
    training_labels = training_df[label_column]
    print(training_df.head())

    print("--------------------------")
    print("TEST DATA SUMMARY:")
    generate_histogram(test_df, label_column)
    test_text = test_df[text_column]
    test_labels = test_df[label_column]

    print("--------------------------")
    print("VECTORIZING...")

    tv = TfidfVectorizer()
    tv.fit(training_text)
    print("FEATURES / TOKENS:", fmt_n(len(tv.get_feature_names())))

    training_matrix = tv.transform(training_text)
    print("FEATURE MATRIX (TRAIN):", type(training_matrix), training_matrix.shape)

    test_matrix = tv.transform(test_text)
    print("FEATURE MATRIX (TEST):", type(test_matrix), test_matrix.shape)

    #
    # MODELS (CUSTOM PIPELINE)
    #

    models = {
        "logistic_regression": LogisticRegression(random_state=99),
        "multinomial_nb": MultinomialNB()
    }

    for model_name in models.keys():
        model = models[model_name]
        print("--------------------------")
        print(f"{model_name.upper()}...")
        print(model)
        print("TRAINING...")
        job = Job()
        job.start()
        model.fit(training_matrix, training_labels)
        job.end()

        print("TRAINING SCORES...")
        training_predictions = model.predict(training_matrix)
        training_scores = classification_report(training_labels, training_predictions, output_dict=True)
        print("ACCY:", training_scores["accuracy"])
        pprint(training_scores)

        print("TEST SCORES...")
        test_predictions = model.predict(test_matrix)
        test_scores = classification_report(test_labels, test_predictions, output_dict=True)
        print("ACCY:", test_scores["accuracy"])
        pprint(test_scores)


        #print("SAVING MODEL FILES...")
        #model_id = ("dev" if APP_ENV == "development" else datetime.now().strftime("%Y-%m-%d-%H%M")) # overwrite same model in development
        #storage = ModelStorage(dirpath=f"{MODELS_DIRPATH}/{model_name}/{model_id}")
        #storage.save_vectorizer(tv)
        #storage.save_model(model)
        #storage.save_scores({
        #    "model_name": model_name,
        #    "model_id": model_id,
        #    "features": len(tv.get_feature_names()),
        #    "training_matrix": training_matrix.shape,
        #    "test_matrix": test_matrix.shape,
        #    "training_scores": training_scores,
        #    "test_scores": test_scores
        #})
