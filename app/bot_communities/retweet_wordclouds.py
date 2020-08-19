import os
#from pprint import pprint
from collections import Counter

import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
#import spacy
from spacy.tokenizer import Tokenizer

import matplotlib.pyplot as plt
import squarify

from app import APP_ENV, seek_confirmation
from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher
from app.bot_communities.clustering import K_COMMUNITIES
#from app.decorators.datetime_decorators import dt_to_s, logstamp, dt_to_date, s_to_dt
#from app.decorators.number_decorators import fmt_n

ALPHANUMERIC_PATTERN = r'[^a-zA-Z ^0-9]'  # same as "[^a-zA-Z ^0-9]"

#class CloudMaker:
#    def __init__(self):
#        self.ps = PorterStemmer()
#        self.stop_words = stopwords.words("english")

ps = PorterStemmer()
stop_words = stopwords.words("english")

def tokenize(doc):
    """
    Params: doc (str) the document to tokenize
    Returns: a list of tokens like ["___", "_____", "____"]
    """
    doc = doc.lower() # normalize case
    doc = re.sub(ALPHANUMERIC_PATTERN, "", doc)  # keep only alphanumeric characters
    tokens = doc.split()
    return [ps.stem(token) for token in tokens if token not in stop_words] # stem and remove stopwords


def summarize(token_sets):
    """
    Param: token_sets a list of token lists
    """

    print("COMPILING TOKEN SUMMARY TABLE...")
    token_counter = Counter()
    doc_counter = Counter()

    for tokens in token_sets:
        token_counter.update(tokens)
        # removes duplicate tokens so they only get counted once per doc!
        doc_counter.update(set(tokens))

    token_counts = zip(token_counter.keys(), token_counter.values())
    doc_counts = zip(doc_counter.keys(), doc_counter.values())

    token_df = pd.DataFrame(token_counts, columns=["token", "count"])
    doc_df = pd.DataFrame(doc_counts, columns=["token", "doc_count"])

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

    ordered_columns = ["token", "rank", "count",
                       "pct", "running_pct", "doc_count", "doc_pct"]
    return df.reindex(columns=ordered_columns).sort_values(by="rank")


def plot_top_tokens(token_sets):
    summary_table = summarize(token_sets)
    top_tokens_table = summary_table[summary_table["rank"] <= 20]
    print("PLOTTING TOP TOKENS...")

    #sns.distplot(summary_table["pct"])
    #plt.show()

    squarify.plot(sizes=top_tokens_table["pct"],
                  label=top_tokens_table["token"], alpha=0.8)
    plt.axis("off")
    plt.show()



if __name__ == "__main__":

    print("----------------")
    print("K COMMUNITIES:", K_COMMUNITIES)

    grapher = BotRetweetGrapher()
    local_dirpath = os.path.join(grapher.local_dirpath, "k_communities", str(K_COMMUNITIES)) # dir should be already made by cluster maker
    local_csv_filepath = os.path.join(local_dirpath, "retweets.csv")
    print(os.path.abspath(local_csv_filepath))
    if not os.path.exists(local_dirpath):
        os.makedirs(local_dirpath)

    print("----------------")
    print("LOADING RETWEETS:")
    df = pd.read_csv(local_csv_filepath)
    print(df.head())

    seek_confirmation()

    # TODO...

    # for each date
    date = "2020-01-01"
    local_wordclouds_dirpath = os.path.join(local_dirpath, "wordclouds", date)
    if not os.path.exists(local_wordclouds_dirpath):
        os.makedirs(local_wordclouds_dirpath)

    # for each community
    community_id = 0
    local_wordcloud_filepath = os.path.join(local_wordclouds_dirpath, f"community-{community_id}.png")
    print(os.path.abspath(local_wordcloud_filepath))



    breakpoint()

    #print(df[["reviews.rating", "reviews.text"]])
    #print("REVIEW RATINGS...")
    #print(df["reviews.rating"].value_counts())
#
    #print("REVIEW TEXT...")
    #print(df["reviews.text"].str.len().value_counts())

    tokens = df["status_text"].apply(lambda txt: tokenize(txt))
    print(tokens[0:5])
    plot_top_tokens(df["nlp.tokens"].values.tolist())
