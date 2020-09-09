import os

from app import seek_confirmation
from app.nlp.model_storage import ModelStorage, BEST_MODEL_DIRPATH

if __name__ == "__main__":

    storage = ModelStorage(dirpath=BEST_MODEL_DIRPATH)

    tv = storage.load_vectorizer()
    print(type(tv))
    print("FEATURES / TOKENS:", len(tv.get_feature_names())) #> 3842

    clf = storage.load_model()
    print(type(clf))


    while True:

        status_text = input("Status Text: ") or "Hello 123"

        matrix = tv.transform([status_text])
        #print(matrix)

        result = clf.predict(matrix)
        print("PREDICTED COMMUNITY ID:", result[0])

        seek_confirmation()
