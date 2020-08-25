
import os
from functools import lru_cache
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
#from threading import current_thread #, #Thread, Lock, BoundedSemaphore

from dotenv import load_dotenv
from pandas import DataFrame, to_datetime
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import logstamp, s_to_date
from app.decorators.number_decorators import fmt_n
from app.bot_communities.csv_storage import LocalStorage
from app.bot_communities.retweet_analyzer import RetweetsAnalyzer

from app.bot_communities.tokenizers import SpacyTokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies, train_topic_model, parse_topics, LdaMulticore

load_dotenv()

START_DATE = os.getenv("START_DATE", default="2019-12-12")
END_DATE = os.getenv("END_DATE", default="2020-02-20")

MAX_THREADS = int(os.getenv("MAX_THREADS", default=10))
MULTIPROCESS = (os.getenv("MULTIPROCESS", default="true") == "true")

class DailyRetweetsAnalyzer(RetweetsAnalyzer):
    def __init__(self, community_id, community_retweets_df, parent_dirpath, date, tokenize=None):
        local_dirpath = os.path.join(parent_dirpath, f"community-{community_id}", "daily")
        self.date = date
        tokenize = tokenize or SpacyTokenizer().custom_stem_lemmas
        super().__init__(community_id, community_retweets_df, local_dirpath, tokenize)

    def customize_paths_and_titles(self):
        self.most_retweets_chart_filepath = os.path.join(self.local_dirpath, f"most-retweets-{self.date}.png")
        self.most_retweets_chart_title = f"Users with Most Retweets from Bot Community {self.community_id} on {self.date}"

        self.most_retweeters_chart_filepath = os.path.join(self.local_dirpath, f"most-retweeters-{self.date}.png")
        self.most_retweeters_chart_title = f"Users with Most Retweeters from Bot Community {self.community_id} on {self.date}"

        self.top_tokens_csv_filepath = os.path.join(self.local_dirpath, f"top-tokens-{self.date}.csv")
        self.top_tokens_wordcloud_filepath = os.path.join(self.local_dirpath, f"top-tokens-{self.date}-wordcloud.png")
        self.top_tokens_wordcloud_title = f"Word Cloud for Community {self.community_id} on {self.date} (n={fmt_n(len(self.community_retweets_df))})"

        self.topics_csv_filepath = os.path.join(self.local_dirpath, f"topics-{self.date}.csv")


def perform(group_name, filtered_df, parent_dirpath):
    community_id = group_name[0]
    date = group_name[1]
    local_dirpath = os.path.join(parent_dirpath, f"community-{community_id}")

    print("----------------")
    print(logstamp(), "COMMUNITY", community_id, "| DATE:", date, "| RETWEETS:", fmt_n(len(filtered_df)), local_dirpath)

    #time.sleep(3)

    analyzer = DailyRetweetsAnalyzer(community_id, filtered_df, local_dirpath, date)

    analyzer.generate_most_retweets_chart()
    analyzer.generate_most_retweeters_chart()

    analyzer.top_tokens_df
    analyzer.save_top_tokens()
    analyzer.generate_top_tokens_wordcloud()

    analyzer.topics_df
    analyzer.save_topics()


if __name__ == "__main__":

    print("------------------------")
    print("DAILY COMMUNITY RETWEETS ANALYSIS...")
    print("  MULTI-PROCESSING:", MULTIPROCESS)
    print("  MAX PROCESSES:", MAX_THREADS)
    print("  START DATE:", START_DATE)
    print("  END DATE:", END_DATE)

    storage = LocalStorage()
    storage.load_retweets()
    df = storage.retweets_df
    print(df.head())

    seek_confirmation()

    print("----------------")
    print("TRANSFORMING RETWEETS...")
    df["status_created_date"] = df["status_created_at"].apply(s_to_date)
    df["status_created_dt"] = to_datetime(df["status_created_at"])

    print("----------------")
    print("FILTERING RETWEETS...")

    df = df.query(f"{START_DATE.replace('-','')} < status_created_dt < {END_DATE.replace('-','')}") # dashes are for humans, not dataframe queries apparently
    print(df["status_created_date"].value_counts())

    seek_confirmation()

    groupby = storage.retweets_df.groupby(["community_id", "status_created_date"])

    if MULTIPROCESS:
        with ProcessPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(perform, group_name, filtered_df, storage.local_dirpath) for group_name, filtered_df in groupby]
            for future in as_completed(futures):
                result = future.result()
    else:
        for group_name, filtered_df in groupby:
            perform(group_name, filtered_df, storage.local_dirpath)

    print("----------------")
    print("ALL PROCESSES COMPLETE!")
