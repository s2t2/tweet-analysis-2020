import os
import pickle

from memory_profiler import profile

from app import DATA_DIR
from app.file_storage import FileStorage

MODELS_DIRPATH = "tweet_classifier/models" # os.path.join(DATA_DIR, "tweet_classifier", "models")

class ModelStorage(FileStorage):
    def  __init__(self, dirpath=f"{MODELS_DIRPATH}/example"):
        super().__init__(dirpath=dirpath)

        self.local_model_filepath = os.path.join(self.local_dirpath, "model.gpickle")
        self.gcs_model_filepath = os.path.join(self.gcs_dirpath, "model.gpickle")

        self.local_vectorizer_filepath = os.path.join(self.local_dirpath, "vectorizer.gpickle")
        self.gcs_vectorizer_filepath = os.path.join(self.gcs_dirpath, "vectorizer.gpickle")

    #
    # LOCAL STORAGE
    #

    def write_model(self, model):
        print("WRITING MODEL TO LOCAL FILE...")
        with open(self.local_model_filepath, "wb") as f:
            pickle.dump(model, f)

    def read_model(self):
        print("READING MODEL FROM LOCAL FILE...")
        with open(self.local_model_filepath, "rb") as f:
            return pickle.load(f)

    def write_vectorizer(self, vectorizer):
        print("WRITING VECTORIZER TO LOCAL FILE...")
        with open(self.local_vectorizer_filepath, "wb") as f:
            pickle.dump(vectorizer, f)

    def read_vectorizer(self):
        print("READING VECTORIZER FROM LOCAL FILE...")
        with open(self.local_vectorizer_filepath, "rb") as f:
            return pickle.load(f)

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

    #
    # CONVENIENCE METHODS
    #

    def save_model(self, model):
        self.write_model(model)
        if self.wifi:
            self.upload_model()

    @profile
    def load_model(self):
        """Assumes the model already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_model_filepath):
            self.download_model()
        return self.read_model()

    def save_vectorizer(self, vectorizer):
        self.write_vectorizer(vectorizer)
        if self.wifi:
            self.upload_vectorizer()

    @profile
    def load_vectorizer(self):
        """Assumes the vectorizer already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_vectorizer_filepath):
            self.download_vectorizer()
        return self.read_vectorizer()


if __name__ == "__main__":

    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import TfidfVectorizer

    storage = ModelStorage()

    tv = TfidfVectorizer()
    storage.save_vectorizer(tv)

    model = LogisticRegression()
    storage.save_model(model)

    same_tv = storage.load_vectorizer()
    print(type(same_tv))

    same_model = storage.load_model()
    print(type(same_model))


    # TODO: look at all models and ask if we want to promote one to be the "current_best"
