
import os
from functools import lru_cache
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
#from threading import current_thread #, #Thread, Lock, BoundedSemaphore

from dotenv import load_dotenv
from pandas import DataFrame
import matplotlib.pyplot as plt
import plotly.express as px
import squarify

from app import APP_ENV, seek_confirmation
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.bot_communities.csv_storage import LocalStorage
from app.bot_communities.retweet_analyzer import RetweetsAnalyzer

from app.bot_communities.tokenizers import Tokenizer
from app.bot_communities.token_analyzer import summarize_token_frequencies, train_topic_model, parse_topics, LdaMulticore

load_dotenv()

MAX_THREADS = int(os.getenv("MAX_THREADS", default=3))

def perform(community_id, date):
    print(f"COMMUNITY ID: {community_id} | DATE: {date}")


    #community_analyzer = DailyCommunityRetweetsAnalyzer(
    #    community_id=community_id,
    #    community_retweets_df=storage.retweets_df[storage.retweets_df["community_id"] == community_id],
    #    local_dirpath=os.path.join(storage.local_dirpath, f"community-{community_id}")
    #)

    #print("------------------------")
    #print(logstamp(), "COMMUNITY", community_id, "CHARTS...")
    #community_analyzer.generate_most_retweets_chart()
    #community_analyzer.generate_most_retweeters_chart()

    #print("------------------------")
    #print(logstamp(), "COMMUNITY", community_id, "TOKENS...")
    #community_analyzer.top_tokens_df
    #community_analyzer.save_top_tokens()
    #community_analyzer.generate_top_tokens_wordcloud()

    #print("------------------------")
    #print(logstamp(), "COMMUNITY", community_id, "TOPICS...")
    #community_analyzer.topics_df # TODO: taking too long
    #community_analyzer.save_topics() # TODO: taking too long


if __name__ == "__main__":

    storage = LocalStorage()
    storage.load_retweets()
    print(storage.retweets_df.head())

    seek_confirmation()

    with ProcessPoolExecutor(max_workers=MAX_THREADS) as executor:

        date = "2020-01-01"
        futures = [executor.submit(perform, community_id, date) for community_id in storage.retweet_community_ids]

        for future in as_completed(futures):
            result = future.result()
            #print(result)
