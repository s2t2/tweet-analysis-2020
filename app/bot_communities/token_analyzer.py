from collections import Counter

from pandas import DataFrame
from gensim.corpora import Dictionary
from gensim.models.ldamulticore import LdaMulticore
#from gensim.models import TfidfModel

def summarize_token_frequencies(token_sets):
    """
    Param token_sets : a list of tokens for each document in a collection

    Returns a DataFrame with a row per topic and columns for various TF/IDF-related scores.
    """
    print("COMPUTING TOKEN AND DOCUMENT FREQUENCIES...")
    token_counter = Counter()
    doc_counter = Counter()

    for tokens in token_sets:
        token_counter.update(tokens)
        doc_counter.update(set(tokens)) # removes duplicate tokens so they only get counted once per doc!

    token_counts = zip(token_counter.keys(), token_counter.values())
    doc_counts = zip(doc_counter.keys(), doc_counter.values())

    token_df = DataFrame(token_counts, columns=["token", "count"])
    doc_df = DataFrame(doc_counts, columns=["token", "doc_count"])

    df = doc_df.merge(token_df, on="token")

    df["rank"] = df["count"].rank(method="first", ascending=False) # TODO: consider sorting on another metric
    df["pct"] = df["count"] / df["count"].sum()
    df["doc_pct"] = df["doc_count"] / len(token_sets)

    #df = df.sort_values(by="rank")
    #df["running_pct"] = df["pct"].cumsum()

    return df.reindex(columns=["token", "rank", "count", "pct", "doc_count", "doc_pct"]).sort_values(by="rank")


#
# TOPIC MODELING
#

def train_topic_model(token_sets):
    dictionary = Dictionary(token_sets)
    print(type(dictionary)) #> <class 'gensim.corpora.dictionary.Dictionary'>
    bags_of_words = [dictionary.doc2bow(tokens) for tokens in token_sets]
    lda = LdaMulticore(corpus=bags_of_words, id2word=dictionary, random_state=99, passes=1, workers=3)
    print(type(lda))
    return lda

def parse_topics(lda):
    """
    Params: lda (gensim.models.ldamulticore.LdaMulticore) a pre-fit LDA model
    Returns: a list of topic records like... {'impeach': 0.058, 'trump': 0.052, 'gop': 0.042, 'clinton': 0.039, 'commit': 0.037, 'condu': 0.037, 'proper': 0.037, 'defense': 0.037, 'jury': 0.037, 'grand': 0.037}
    """
    parsed_response = []
    topics_response = lda.print_topics()
    for topic_row in topics_response:
        topics = topic_row[1] #> '0.067*"sleep" + 0.067*"got" + 0.067*"went" + 0.067*"until" + 0.067*"to" + 0.067*"tired" + 0.067*"they" + 0.067*"all" + 0.067*"ate" + 0.067*"the"'
        topic_pairs = [s.replace('"', "").split("*") for s in topics.split(" + ")] #> [ ['0.067', 'sleep'], ['0.067', 'got'], [], etc... ]
        doc_topics = {}
        for topic_pair in topic_pairs:
            doc_topics[topic_pair[1]] = float(topic_pair[0])
        #print(doc_topics) #> {'sleep': 0.067, 'got': 0.067, etc}
        parsed_response.append(doc_topics)
    return parsed_response
