


# web_app/services/basilica_service.py

import basilica
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BASILICA_API_KEY")


class BasilicaService:
    def __init__(self):
        self.client = basilica.Connection(API_KEY)

        print("BASILICA SERVICE:")
        print(type(self.client)) #> <class 'basilica.Connection'>

    def embed_tweets_in_batches(self, status_texts):
        return self.client.embed_sentences(status_texts, model="twitter")


if __name__ == "__main__":

    bas = BasilicaService()

    print("---------")
    sentence = "Hello again"
    print(sentence)
    sent_embeddings = bas.client.embed_sentence(sentence)
    print(list(sent_embeddings))

    print("---------")
    sentences = ["Hello world!", "How are you?"]
    print(sentences)
    # it is more efficient to make a single request for all sentences...
    embeddings = bas.client.embed_sentences(sentences)
    print("EMBEDDINGS...")
    print(type(embeddings))
    print(list(embeddings)) # [[0.8556405305862427, ...], ...]
