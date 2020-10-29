
import os
from collections import Counter

from pandas import DataFrame, read_csv
import re

from app.bq_service import BigQueryService
from app.file_storage import FileStorage
from app.job import Job
from app.decorators.number_decorators import fmt_n

LIMIT = os.getenv("LIMIT") # 1000 # None  # os.getenv("LIMIT")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="25_000")) # 100
DESTRUCTIVE = (os.getenv("DESTRUCTIVE", default="false") == "true") # True
TAGS_DESTRUCTIVE = (os.getenv("TAGS_DESTRUCTIVE", default="false") == "true") # True

TWITTER_PATTERN = r'[^a-zA-Z ^0-9 # @]' # alphanumeric, plus hashtag and handle symbols (twitter-specific)

def download_tweets():
    job = Job()
    bq_service = BigQueryService()

    job.start()
    records = []
    for row in bq_service.fetch_statuses_with_tags(limit=LIMIT):
        #print(row)
        records.append(dict(row))

        job.counter +=1
        if job.counter % BATCH_SIZE == 0:
            job.progress_report()
    job.end()

    return DataFrame(records)

def parse_hashtags(status_text):
    txt = re.sub(TWITTER_PATTERN, "", status_text.upper())
    tags = [token.upper() for token in status_text.split() if token.startswith("#") and not token.endswith("#")]
    return tags

def summarize_token_frequencies(tokens_series):
    """
    Param token_sets : a list of tokens for each document in a collection

    Returns a DataFrame with a row per topic and columns for various TF/IDF-related scores.
    """
    print("COMPUTING TOKEN AND DOCUMENT FREQUENCIES...")
    token_counter = Counter()
    doc_counter = Counter()
    my_counter = Counter()

    for tokens in tokens_series:
        token_counter.update(tokens)
        doc_counter.update(set(tokens)) # removes duplicate tokens so they only get counted once per doc!

    token_counts = zip(token_counter.keys(), token_counter.values())
    doc_counts = zip(doc_counter.keys(), doc_counter.values())

    token_df = DataFrame(token_counts, columns=["token", "count"])
    doc_df = DataFrame(doc_counts, columns=["token", "doc_count"])

    df = doc_df.merge(token_df, on="token")

    df["rank"] = df["count"].rank(method="first", ascending=False)
    df["pct"] = df["count"] / df["count"].sum()
    df["doc_pct"] = df["doc_count"] / len(tokens_series)

    #df = df.sort_values(by="rank")
    #df["running_pct"] = df["pct"].cumsum()

    return df.reindex(columns=["token", "rank", "count", "pct", "doc_count", "doc_pct"]).sort_values(by="rank")


if __name__ == "__main__":

    storage = FileStorage(dirpath="bot_analysis")



    tweets_csv_filepath = os.path.join(storage.local_dirpath, "statuses_with_tags.csv")
    if os.path.isfile(tweets_csv_filepath) and not DESTRUCTIVE:
        print("LOADING TWEETS...")
        tweets_df = read_csv(tweets_csv_filepath)
    else:
        print("DOWNLOADING TWEETS...")
        tweets_df = download_tweets()
        tweets_df.to_csv(tweets_csv_filepath, index=False)
    print(fmt_n(len(tweets_df)))
    print(tweets_df.head())



    print("TOKENIZING TWEETS...")
    #tweets_df["status_tags"] = tweets_df["status_text"].apply(parse_hashtags)
    tweets_df["status_tags"] = tweets_df["status_text"].map(parse_hashtags)



    tags_csv_filepath = os.path.join(storage.local_dirpath, "top_status_tags.csv")
    top_tags_csv_filepath = os.path.join(storage.local_dirpath, "top_1000_status_tags.csv")
    if os.path.isfile(tags_csv_filepath) and not TAGS_DESTRUCTIVE:
        print("LOADING TOP TAGS...")
        tags_df = read_csv(tags_csv_filepath)
    else:
        print("SUMMARIZING...")
        tags_df = summarize_token_frequencies(tweets_df["status_tags"])
        tags_df.to_csv(tags_csv_filepath, index=False)
        tags_df.head(1000).to_csv(top_tags_csv_filepath, index=False)
    print(tags_df.head())



    for is_bot, filtered_df in tweets_df.groupby(["is_bot"]):
        bot_or_human = {True: "bot", False: "human"}[is_bot]
        print(bot_or_human.upper())

        bh_tags_df = summarize_token_frequencies(filtered_df["status_tags"])
        print(bh_tags_df.head())

        bh_tags_csv_filepath = os.path.join(storage.local_dirpath, f"top_{bot_or_human}_status_tags.csv")
        bh_top_tags_csv_filepath = os.path.join(storage.local_dirpath, f"top_1000_{bot_or_human}_status_tags.csv")
        bh_tags_df.to_csv(bh_tags_csv_filepath, index=False)
        bh_tags_df.head(1000).to_csv(bh_top_tags_csv_filepath, index=False)
