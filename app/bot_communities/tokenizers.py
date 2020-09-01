import os
from collections import Counter
from functools import lru_cache
from pprint import pprint

import re
from dotenv import load_dotenv
from pandas import DataFrame
from nltk.corpus import stopwords as NLTK_STOPWORDS
from gensim.parsing.preprocessing import STOPWORDS as GENSIM_STOPWORDS
from spacy.lang.en.stop_words import STOP_WORDS as SPACY_STOP_WORDS
#from spacy.tokenizer import Tokenizer
import spacy
from nltk.stem import PorterStemmer

load_dotenv()

MODEL_SIZE = os.getenv("MODEL_SIZE", default="sm")  # sm, md, lg

CUSTOM_STOP_WORDS = {
    "rt", "httpstco", "amp", # twitter / tweet stuff
    "today", "tonight", "tomorrow", "time", "ago",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "want", "wants", "like", "get", "go", "say", "says", "told",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "th", "im", "hes", "hi", "thi",
    # impeachment-specific stopwords
    "rep", "president", "presidents", "col",
    #"impeach", "impeachment", "impeached",
    # "trump", "articles", "trial", "house", "senate"
}

ALPHANUMERIC_PATTERN = r'[^a-zA-Z ^0-9]' # alphanumeric only (strict)
TWITTER_ALPHANUMERIC_PATTERN = r'[^a-zA-Z ^0-9 # @]' # alphanumeric, plus hashtag and handle symbols (twitter-specific)

class CustomStemmer():
    def stem(self, token):
        if token in ["impeachment", "impeached"]:
            token = "impeach"
        if token == "trumps":
            token = "trump"
        if token == "pelosis":
            token = "pelosi"
        if token == "democrats":
            token = "democrat"
        if token == "republicans":
            token = "republican"
        return token

class Tokenizer():

    def __init__(self):
        self.porter_stemmer = PorterStemmer()
        self.custom_stemmer = CustomStemmer()

    @property
    @lru_cache(maxsize=None)
    def stop_words(self):
        words = set(NLTK_STOPWORDS.words("english")) | SPACY_STOP_WORDS | GENSIM_STOPWORDS | CUSTOM_STOP_WORDS
        words |= set([word.replace("'","") for word in words if "'" in word]) # contraction-less: "don't" -> "dont"
        return words

    def basic_tokens(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        return tokens

    def porter_stems(self, txt):
        tokens = self.basic_tokens(txt)
        stems = [self.porter_stemmer.stem(token) for token in tokens]  # custom word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

    def custom_stems(self, txt):
        tokens = self.basic_tokens(txt)
        stems = [self.custom_stemmer.stem(token) for token in tokens]  # custom word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

    def hashtags(self, txt):
        txt = re.sub(TWITTER_ALPHANUMERIC_PATTERN, "", txt.upper())
        tags = [token for token in txt.split() if token.startswith("#") and not token.endswith("#")]
        return tags

    def handles(self, txt):
        txt = re.sub(TWITTER_ALPHANUMERIC_PATTERN, "", txt.upper())
        handlez = [token for token in txt.split() if token.startswith("@") and not token.endswith("@")]
        return handlez


class SpacyTokenizer(Tokenizer):

    def __init__(self, model_size=MODEL_SIZE):
        super().__init__()
        self.model_name = f"en_core_web_{model_size}"
        self.nlp = spacy.load(self.model_name)

        print("SPACY TOKENIZER:", type(self.nlp), self.model_name.upper())

    def custom_stem_lemmas(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters

        doc = self.nlp(txt)  #> <class 'spacy.tokens.doc.Doc'>
        tokens = [token for token in doc if token.is_punct == False and token.is_space == False]
        tokens = [token for token in tokens if token.is_stop == False and str(token) not in self.stop_words] # double stopword removal!!!
        lemmas = [token.lemma_.lower() for token in tokens]
        lemmas = [self.custom_stemmer.stem(lemma) for lemma in lemmas]
        return [lemma for lemma in lemmas if lemma not in self.stop_words]

    def entity_tokens(self, txt):
        doc = self.nlp(txt) #> <class 'spacy.tokens.doc.Doc'>
        return doc.ents


if __name__ == "__main__":
    print("----------------")
    status_text = "Welcome to New York. Welcoming isn't it? :-D"
    print(status_text)

    print("----------------")
    tokenizer = Tokenizer()
    print(type(tokenizer))
    print(len(tokenizer.stop_words))
    print("  basic_tokens:", tokenizer.basic_tokens(status_text))
    print("  porter_stems:", tokenizer.porter_stems(status_text))
    print("  custom_stems:", tokenizer.custom_stems(status_text))

    print("----------------")
    tokenizer = SpacyTokenizer()
    print(type(tokenizer))
    print(len(tokenizer.stop_words))
    print("  custom_stem_lemmas:", tokenizer.custom_stem_lemmas(status_text))
    print("  entity_tokens:", tokenizer.entity_tokens(status_text))
