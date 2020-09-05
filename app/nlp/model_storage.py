import os
import pickle

from app import DATA_DIR

MODELS_DIRPATH = os.path.join(DATA_DIR, "user_communities", "n_communities", str(2), "tweet_classifier", "models")

def save_model(model, local_filepath):
    print("SAVING MODEL TO LOCAL FILE...")
    with open(local_filepath, "wb") as f:
        pickle.dump(model, f)

def load_model(local_filepath):
    print("LOADING MODEL FROM LOCAL FILE...")
    with open(local_filepath, "rb") as f:
        model = pickle.load(f)
    return model


if __name__ == "__main__":

    from sklearn.linear_model import LogisticRegression

    clf = LogisticRegression()
    print(type(clf))

    local_filepath = os.path.join(MODELS_DIRPATH, "example.gpickle")

    save_model(clf, local_filepath)

    clf = load_model(local_filepath)
    print(type(clf))
