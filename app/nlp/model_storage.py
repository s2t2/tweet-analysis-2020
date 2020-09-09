import os
import pickle
import json
from pprint import pprint

from memory_profiler import profile

from app import DATA_DIR, seek_confirmation
from app.file_storage import FileStorage
from app.decorators.datetime_decorators import logstamp

MODELS_DIRPATH = "tweet_classifier/models" # os.path.join(DATA_DIR, "tweet_classifier", "models")
EXAMPLE_MODEL_DIRPATH = f"{MODELS_DIRPATH}/example"
BEST_MODEL_DIRPATH = f"{MODELS_DIRPATH}/current_best"

class ModelStorage(FileStorage):
    def  __init__(self, dirpath=EXAMPLE_MODEL_DIRPATH):
        super().__init__(dirpath=dirpath)

        self.local_model_filepath = os.path.join(self.local_dirpath, "model.gpickle")
        self.gcs_model_filepath = os.path.join(self.gcs_dirpath, "model.gpickle")

        self.local_vectorizer_filepath = os.path.join(self.local_dirpath, "vectorizer.gpickle")
        self.gcs_vectorizer_filepath = os.path.join(self.gcs_dirpath, "vectorizer.gpickle")

        self.local_scores_filepath = os.path.join(self.local_dirpath, "scores.json")
        self.gcs_scores_filepath = os.path.join(self.gcs_dirpath, "scores.json")

    #
    # LOCAL STORAGE
    #

    def write_model(self, model):
        print(logstamp(), "WRITING MODEL TO LOCAL FILE...")
        with open(self.local_model_filepath, "wb") as f:
            pickle.dump(model, f)

    def read_model(self):
        print(logstamp(), "READING MODEL FROM LOCAL FILE...")
        with open(self.local_model_filepath, "rb") as f:
            return pickle.load(f)

    def write_vectorizer(self, vectorizer):
        print(logstamp(), "WRITING VECTORIZER TO LOCAL FILE...")
        with open(self.local_vectorizer_filepath, "wb") as f:
            pickle.dump(vectorizer, f)

    def read_vectorizer(self):
        print(logstamp(), "READING VECTORIZER FROM LOCAL FILE...")
        with open(self.local_vectorizer_filepath, "rb") as f:
            return pickle.load(f)

    def write_scores(self, scores):
        print(logstamp(), "WRITING SCORES TO LOCAL FILE...")
        with open(self.local_scores_filepath, "w") as f:
            json.dump(scores, f)

    #
    # REMOTE STORAGE
    #

    def upload_model(self):
        self.upload_file(self.local_model_filepath, self.gcs_model_filepath)

    def download_model(self):
        self.upload_file(self.gcs_model_filepath, self.local_model_filepath)

    def upload_vectorizer(self):
        self.upload_file(self.local_vectorizer_filepath, self.gcs_vectorizer_filepath)

    def download_vectorizer(self):
        self.upload_file(self.gcs_vectorizer_filepath, self.local_vectorizer_filepath)

    def upload_scores(self):
        self.upload_file(self.local_scores_filepath, self.gcs_scores_filepath)

    #
    # CONVENIENCE METHODS
    #

    def save_model(self, model):
        self.write_model(model)
        if self.wifi:
            self.upload_model()

    #@profile
    def load_model(self):
        """Assumes the model already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_model_filepath):
            self.download_model()
        return self.read_model()

    def save_vectorizer(self, vectorizer):
        self.write_vectorizer(vectorizer)
        if self.wifi:
            self.upload_vectorizer()

    #@profile
    def load_vectorizer(self):
        """Assumes the vectorizer already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_vectorizer_filepath):
            self.download_vectorizer()
        return self.read_vectorizer()

    def save_scores(self, scores):
        self.write_scores(scores)
        if self.wifi:
            self.upload_scores()

    #
    # MODEL PROMOTION
    #

    def promote_model(self, destination=BEST_MODEL_DIRPATH):
        # 'tweet_classifier/models/logistic_regression/2020-09-08-1229'

        # copy local dirpath to best

        # copy remote dirpath

        blobs = list(self.gcs_service.bucket.list_blobs())
        matching_blobs = [blob for blob in blobs if self.dirpath in blob.name]
        print("MODEL FILES TO PROMOTE...")
        pprint(matching_blobs)
        seek_confirmation()

        print("PROMOTING MODEL FILES...")
        for blob in matching_blobs:
            file_name = blob.name.split("/")[-1] #> 'model.gpickle'
            new_path = self.compile_gcs_dirpath(f"{destination}/{file_name}") #f"storage/data/{destination}/{file_name}"
            self.gcs_service.bucket.copy_blob(blob, destination_bucket=self.gcs_service.bucket, new_name=new_path)





if __name__ == "__main__":

    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import TfidfVectorizer

    storage = ModelStorage()

    tv = TfidfVectorizer()
    storage.save_vectorizer(tv)

    model = LogisticRegression()
    storage.save_model(model)
    storage.save_scores({"accy":0.999, "features": 100})

    same_tv = storage.load_vectorizer()
    print(type(same_tv))

    same_model = storage.load_model()
    print(type(same_model))


    # TODO: look at all models and ask if we want to promote one to be the "current_best"
