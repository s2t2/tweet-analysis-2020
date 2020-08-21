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

class TokenMaker:

    @property
    @lru_cache(maxsize=None)
    def stop_words(self):
        words = NLTK_STOPWORDS | SPACY_STOP_WORDS | GENSIM_STOPWORDS | self.custom_stop_words
        words |= set([word.replace("'","") for word in words if "'" in word]) # contraction-less: "don't" -> "dont"
        return words

    @property
    @lru_cache(maxsize=None)
    def custom_stop_words(self):
        """OVERWRITE / MERGE IN CHILD CLASS AS DESIRED"""
        return {
            "rt", "httpstco", "amp", # twitter / tweet stuff
            "today", "tonight", "tomorrow", "time", "ago",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "want", "wants", "like", "get", "go", "say", "says", "told",
            "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "th", "im", "hes", "hi", "thi",
        }

    def custom_stem(self, token):
        """OVERWRITE IN CHILD CLASS AS DESIRED"""
        return token

    @property
    @lru_cache(maxsize=None)
    def ps(self):
        stemmer = PorterStemmer()
        print("PORTER STEMMER", type(stemmer))
        return stemmer

    @property
    @lru_cache(maxsize=None)
    def nlp(self):
        self.model_name = f"en_core_web_{MODEL_SIZE}"
        print("LOADING SPACY MODEL", self.model_name.upper())
        model = spacy.load(self.model_name)
        print(type(model))
        return model

    #
    # COMPETING TOKENIZATION FUNCTIONS
    #

    def tokenize_basic(self, txt):
        txt = txt.lower() # normalize case
        txt = txt.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        return tokens

    def tokenize_porter_stems(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        stems = [ps.stem(token) for token in tokens]  # word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

    def tokenize_custom_stems(self, txt):
        txt = txt.lower() # normalize case
        txt = re.sub(ALPHANUMERIC_PATTERN, "", txt)  # keep only alphanumeric characters
        tokens = txt.split()
        tokens = [token for token in tokens if token not in self.stop_words] # remove stopwords
        stems = [self.custom_stem(token) for token in tokens]  # custom word stems only
        stems = [stem for stem in stems if stem not in self.stop_words] # remove stopwords again
        return stems

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

    def summarize(self, token_sets):
        print("COMPILING TOKEN SUMMARY TABLE...")
        token_counter = Counter()
        doc_counter = Counter()

        for tokens in token_sets:
            token_counter.update(tokens)
            # removes duplicate tokens so they only get counted once per doc!
            doc_counter.update(set(tokens))

        token_counts = zip(token_counter.keys(), token_counter.values())
        doc_counts = zip(doc_counter.keys(), doc_counter.values())

        token_df = DataFrame(token_counts, columns=["token", "count"])
        doc_df = DataFrame(doc_counts, columns=["token", "doc_count"])

        df = doc_df.merge(token_df, on="token")
        total_tokens = df["count"].sum()
        total_docs = len(token_sets)

        df["rank"] = df["count"].rank(method="first", ascending=False)

        # df["token_count"].apply(lambda x: x / total_tokens)
        df["pct"] = df["count"] / total_tokens

        df = df.sort_values(by="rank")
        df["running_pct"] = df["pct"].cumsum()

        # df["doc_count"].apply(lambda x: x / total_docs)
        df["doc_pct"] = df["doc_count"] / total_docs

        ordered_columns = ["token", "rank", "count", "pct", "running_pct", "doc_count", "doc_pct"]
        return df.reindex(columns=ordered_columns).sort_values(by="rank")

    def topic_model(self, token_sets):
        dictionary = Dictionary(token_sets)
        bags_of_words = [dictionary.doc2bow(tokens) for tokens in token_sets]
        lda = LdaMulticore(corpus=bags_of_words, id2word=dictionary, random_state=99, passes=10, workers=4)
        response = lda.print_topics()
        breakpoint()


class CustomTokenMaker(TokenMaker):

    def tokenize(self, txt):
        return self.tokenize_spacy_lemmas_custom_stems(txt)

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
