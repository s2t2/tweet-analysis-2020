from collections import Counter

from pandas import DataFrame

def summarize_token_frequencies(self, token_sets):
    """
    Param token_sets : a list of tokens for each document in a collection
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

    df["rank"] = df["count"].rank(method="first", ascending=False)
    df["pct"] = df["count"] / df["count"].sum()
    df["doc_pct"] = df["doc_count"] / len(token_sets)

    #df = df.sort_values(by="rank")
    #df["running_pct"] = df["pct"].cumsum()

    return df.reindex(columns=["token", "rank", "count", "pct", "doc_count", "doc_pct"]).sort_values(by="rank")


#def topic_model(self, token_sets):
#    dictionary = Dictionary(token_sets)
#    bags_of_words = [dictionary.doc2bow(tokens) for tokens in token_sets]
#    lda = LdaMulticore(corpus=bags_of_words, id2word=dictionary, random_state=99, passes=10, workers=4)
#    response = lda.print_topics()
#    breakpoint()
