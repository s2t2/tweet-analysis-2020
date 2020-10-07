
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

import matplotlib.pyplot as plt

from app import APP_ENV, DATA_DIR, seek_confirmation
#from app.job import Job
from app.decorators.number_decorators import fmt_n
#from app.bq_service import BigQueryService
from app.nlp.model_storage import ModelStorage

NLP_DIR = os.path.join(DATA_DIR, "nlp_v2")

def three_community_labels(score):
    if 0 < score and score < 1:
        score = 0.5
    return score

def three_community_labels_v2(score):
    if score < 0.3:
        label = "D"
    elif score > 0.7:
        label = "R"
    else:
        label = "U"
    return label

def two_community_party_labels(score):
    if score <= 0.5:
        label = "D"
    else:
        label = "R"
    return label

def generate_histogram(df, label_column, img_filepath=None, show_img=False, title="Data Labels"):
    #print("ROWS:", fmt_n(len(df)))
    #print(df.head())
    #print("VALUE COUNTS:")
    print(df[label_column].value_counts())

    labels = df[label_column]

    plt.grid()
    plt.title(title)
    plt.hist(labels, color="grey")
    plt.xlabel("Label")
    plt.ylabel("Frequency")

    if img_filepath:
        plt.savefig(img_filepath)

    #show_img = show_img or (APP_ENV == "development")
    if show_img:
        plt.show()

    plt.clf()  # clear the figure, to prevent topic text overlapping from previous plots

class Trainer:
    def __init__(self):
        self.text_column = "status_text"

        self.raw_label_column = "avg_community_score"
        self.label_maker = two_community_party_labels #vanity_labels # squish_the_middle
        self.label_column = "community_label"

        self.df = None

        self.df_train = None
        self.df_test = None

        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None

        self.tv = None
        self.matrix_train = None
        self.matrix_test = None

    def load_data(self):
        print("--------------------------")
        print("LOADING LABELED DATA...")
        self.df = read_csv(os.path.join(NLP_DIR, "2_community_labeled_status_texts.csv"))
        generate_histogram(self.df, self.raw_label_column, title="Raw Data Labels", img_filepath=os.path.join(NLP_DIR, "raw_histogram.png"))

        df_middle = self.df[(self.df[self.raw_label_column] > 0) & (self.df[self.raw_label_column] < 1)]
        generate_histogram(df_middle, self.raw_label_column, title="Raw Data Labels (Excluding 0 and 1)", img_filepath=os.path.join(NLP_DIR, "raw_histogram_middle.png"))

        #def process_data(self):
        print("--------------------------")
        print("PRE-PROCESSING...")

        # If you leave some of the 1 count labels in, when you try to stratify, you'll get ValueError: The least populated class in y has only 1 member, which is too few. The minimum number of groups for any class cannot be less than 2.
        # So let's take all the statuses with a score in-between 0 and 1, and give them a label of 0.5 (not sure)
        self.df[self.label_column] = self.df[self.raw_label_column].apply(self.label_maker)

        # Need to convert floats to integers or else Logistic Regression will raise ValueError: Unknown label type: 'continuous'
        #self.df[self.label_column] = self.df[self.label_column].astype(str) # convert to categorical

        generate_histogram(self.df, self.label_column, title="Training Data", img_filepath=os.path.join(NLP_DIR, "training_data_histogram.png"))

    def split_data(self):
        print("--------------------------")
        print("SPLITTING...")
        self.df_train, self.df_test = train_test_split(self.df, stratify=self.df[self.label_column], test_size=0.2, random_state=99)

        print("--------------------------")
        print("TRAIN:")
        print(self.df_train.head())
        generate_histogram(self.df_train, self.label_column) # should ideally be around equal for each class!

        self.x_train = self.df_train[self.text_column]
        self.y_train = self.df_train[self.label_column]

        #print("--------------------------")
        #print("TEST:")
        #generate_histogram(self.df_test, self.label_column) # should have same dist

        self.x_test = self.df_test[self.text_column]
        self.y_test = self.df_test[self.label_column]

    def vectorize(self):
        print("--------------------------")
        print("VECTORIZING...")

        self.tv = TfidfVectorizer()
        self.tv.fit(self.x_train)
        print("FEATURES / TOKENS:", fmt_n(len(self.tv.get_feature_names())))

        self.matrix_train = self.tv.transform(self.x_train)
        print("FEATURE MATRIX (TRAIN):", type(self.matrix_train), self.matrix_train.shape)

        self.matrix_test = self.tv.transform(self.x_test)
        print("FEATURE MATRIX (TEST):", type(self.matrix_test), self.matrix_test.shape)

    def train_and_score_models(self, models=None):
        models = models or {
            "logistic_regression": LogisticRegression(random_state=99),
            "multinomial_nb": MultinomialNB()
        }
        for model_name in models.keys():
            print("--------------------------")
            print("MODEL:")
            model = models[model_name]
            print(model)

            print("TRAINING...")
            model.fit(self.matrix_train, self.y_train)

            print("TRAINING SCORES:")
            y_pred_train = model.predict(self.matrix_train)
            scores_train = classification_report(self.y_train, y_pred_train, output_dict=True)
            print("ACCY:", scores_train["accuracy"])
            pprint(scores_train)

            print("TEST SCORES:")
            y_pred_test = model.predict(self.matrix_test)
            scores_test = classification_report(self.y_test, y_pred_test, output_dict=True)
            print("ACCY:", scores_test["accuracy"])
            pprint(scores_test)

            print("SAVING ...")
            model_id = ("dev" if APP_ENV == "development" else datetime.now().strftime("%Y-%m-%d-%H%M")) # overwrite same model in development
            storage = ModelStorage(dirpath=f"nlp_v2/models/{model_id}/{model_name}")
            storage.save_vectorizer(self.tv)
            storage.save_model(model)
            storage.save_scores({
                "model_name": model_name,
                "model_id": model_id,
                "features": len(self.tv.get_feature_names()),
                "label_maker": self.label_maker.__name__,
                "matrix_train": self.matrix_train.shape,
                "matrix_test": self.matrix_test.shape,
                "scores_train": scores_train,
                "scores_test": scores_test
            })





if __name__ == "__main__":



    trainer = Trainer()

    trainer.load_data()
    trainer.df.drop(["avg_community_score", "status_occurrences"], axis="columns", inplace=True) # just make the df smaller

    trainer.split_data()

    trainer.vectorize()

    trainer.train_and_score_models()
