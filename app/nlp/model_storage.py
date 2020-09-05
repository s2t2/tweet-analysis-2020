import os
import pickle

from memory_profiler import profile

from app import DATA_DIR
from app.file_storage import FileStorage

MODELS_DIRPATH = os.path.join(DATA_DIR, "tweet_classifier", "models")

class ModelStorage(FileStorage):
    def  __init__(self, dirpath=MODELS_DIRPATH, model_name="model.gpickle"):
        super().__init__(dirpath=dirpath)
        self.local_model_filepath = os.path.join(self.local_dirpath, model_name)
        self.gcs_model_filepath = os.path.join(self.gcs_dirpath, model_name)

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

    #
    # REMOTE STORAGE
    #

    def upload_model(self):
        self.upload_file(self.local_model_filepath, self.gcs_model_filepath)

    def download_model(self):
        self.upload_file(self.gcs_model_filepath, self.local_model_filepath)

    #
    # CONVENIENCE METHODS
    #

    def save_model(self, model):
        self.write_model(model)

        if self.wifi:
            self.upload_model()

    @profile
    def load_model(self):
        """Assumes the graph already exists and is saved locally or remotely"""
        if not os.path.isfile(self.local_model_filepath):
            self.download_model()

        return self.read_model()


if __name__ == "__main__":

    from sklearn.linear_model import LogisticRegression

    example_dirpath = os.path.join(MODELS_DIRPATH, "example")
    storage = ModelStorage(dirpath=example_dirpath)

    model = LogisticRegression()
    print(type(model))
    storage.save_model(model)

    same_model = storage.load_model()
    print(type(same_model))
