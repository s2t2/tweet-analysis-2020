import os

from app.nlp.model_storage import ModelStorage

SOURCE = os.getenv("SOURCE", default="nlp_v2/models/dev/multinomial_nb")
DESTINATION = os.getenv("DESTINATION", default="nlp_v2/models/best/multinomial_nb")

if __name__ == "__main__":

    storage = ModelStorage(dirpath=SOURCE)

    storage.promote_model(destination=DESTINATION)
