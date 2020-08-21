import os
from collections import Counter
from functools import lru_cache

import re
from dotenv import load_dotenv
from pandas import DataFrame
from nltk.corpus import stopwords as NLTK_STOPWORDS
from nltk.stem import PorterStemmer
from gensim.parsing.preprocessing import STOPWORDS as GENSIM_STOPWORDS
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as SPACY_STOP_WORDS
#from spacy.tokenizer import Tokenizer

load_dotenv()

MODEL_SIZE = os.getenv("MODEL_SIZE", default="sm")  # sm, md, lg

NLTK_STOPWORDS = set(NLTK_STOPWORDS.words("english"))

ALPHANUMERIC_PATTERN = r'[^a-zA-Z ^0-9]'  # same as "[^a-zA-Z ^0-9]"


class Tokenizer:

    def tokenize(self, txt):
        txt = txt.lower() # normalize case
        txt = txt.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        return tokens

    @property
    @lru_cache(maxsize=None)
    def stop_words(self):
        words = NLTK_STOPWORDS | SPACY_STOP_WORDS | GENSIM_STOPWORDS | self.custom_stop_words
        words |= set([word.replace("'","") for word in words if "'" in word]) # contraction-less: "don't" -> "dont"
        return words

    @property
    @lru_cache(maxsize=None)
    def custom_stop_words(self):
        return {
            "rt", "httpstco", "amp", # twitter / tweet stuff
            "today", "tonight", "tomorrow", "time", "ago",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "want", "wants", "like", "get", "go", "say", "says", "told",
            "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "th", "im", "hes", "hi", "thi",
        }


class CustomTokenizer(Tokenizer):
    """
    A tokenizer for the impeachment dataset, using custom impeachment-related stop-words and stems
    """

    def tokenize(self, txt):
        return self.tokenize_custom_stems(txt)

    def tokenize_custom_stems(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        stems = [self.custom_stem(token) for token in tokens]  # custom word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

    @property
    @lru_cache(maxsize=None)
    def custom_stop_words(self):
        return super().custom_stop_words | {
            "rep", "president", "presidents", "col",
            #"impeach", "impeachment", "impeached",
            # "trump", "articles", "trial", "house", "senate"
        }

    def custom_stem(self, token):
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


class PorterStemTokenizer(ImpeachmentTokenizer):

    def __init__(self):
        super().__init__()
        self.stemmer = PorterStemmer()
        print("PORTER STEMMER", type(self.stemmer))

    def tokenize(self, txt):
        return self.tokenize_porter_stems(txt)

    def tokenize_porter_stems(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        stems = [self.stemmer.stem(token) for token in tokens]  # word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

class SpacyLemmaTokenizer(ImpeachmentTokenizer):

    def __init__(self):
        super().__init__()
        print("LOADING SPACY MODEL...")
        self.model_name = f"en_core_web_{MODEL_SIZE}"
        print(self.model_name.upper())
        self.nlp = spacy.load(self.model_name)
        print(type(self.nlp))

    def tokenize(self, txt):
        return self.tokenize_spacy_lemmas_custom_stems(txt)

    def tokenize_spacy_lemmas_custom_stems(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        doc = self.nlp(txt)  #> <class 'spacy.tokens.doc.Doc'>
        tokens = [token for token in doc if token.is_punct == False and token.is_space == False]
        tokens = [token for token in tokens if token.is_stop == False and str(token) not in self.stop_words] # double stopword removal!!!
        lemmas = [token.lemma_.lower() for token in tokens]
        lemmas = [self.custom_stem(lemma) for lemma in lemmas]
        return [lemma for lemma in lemmas if lemma not in self.stop_words]

    def tokenize_spacy_entities(self, txt):
        #txt = txt.lower() # normalize case
        #txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        doc = nlp(txt) #> <class 'spacy.tokens.doc.Doc'>
        entities = spacy_doc.ents
        breakpoint()
        return entities
