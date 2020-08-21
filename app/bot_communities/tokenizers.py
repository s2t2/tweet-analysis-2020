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

ALPHANUMERIC_PATTERN = r'[^a-zA-Z ^0-9]'  # same as "[^a-zA-Z ^0-9]"

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

    def __init__(self, stop_words=None, stemmer=None):
        self.stop_words = stop_words or self.compile_stop_words()
        self.porter_stemmer = PorterStemmer()
        self.custom_stemmer = CustomStemmer()

    @staticmethod
    def compile_stopwords():
        words = set(NLTK_STOPWORDS.words("english")) | SPACY_STOP_WORDS | GENSIM_STOPWORDS | CUSTOM_STOP_WORDS
        words |= set([word.replace("'","") for word in words if "'" in word]) # contraction-less: "don't" -> "dont"
        return words

    def basic_tokens(self, txt):
        txt = txt.lower() # normalize case
        txt = txt.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
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

class SpacyTokenizer(Tokenizer):

    def __init__(self, stop_words=None, stemmer=None, model_size=MODEL_SIZE):
        super().__init__(stop_words=stop_words, stemmer=stemmer)
        self.nlp = spacy.load(f"en_core_web_{model_size}")
        print(type(self.nlp))

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
        doc = nlp(txt) #> <class 'spacy.tokens.doc.Doc'>
        entities = spacy_doc.ents
        breakpoint()
        return entities


if __name__ == "__main__":
    stop_words = Tokenizer.compile_stopwords()
    print("STOP WORDS...")
    pprint(stop_words)
