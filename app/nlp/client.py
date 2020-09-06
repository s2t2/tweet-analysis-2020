import os

from app.nlp.model_storage import ModelStorage, MODELS_DIRPATH

MODEL_NAME = os.getenv("MODEL_NAME", default="current_best")

if __name__ == "__main__":

    storage = ModelStorage(dirpath=f"{MODELS_DIRPATH}/{MODEL_NAME")

    tv = storage.load_vectorizer()
    print(type(tv))
    print("FEATURES / TOKENS:", len(tv.get_feature_names())) #> 3842

    clf = storage.load_model()
    print(type(clf))

    breakpoint()

    status_text = "Hello 123"

    matrix = tv.transform(status_text)
    print(matrix)

    prediction = clf.predict(matrix)
    print(prediction)

    breakpoint()
