

import os

from dotenv import load_dotenv
from pandas import DataFrame, read_csv, concat

from app import DATA_DIR, seek_confirmation

load_dotenv()

EVENT_NAME = os.getenv("EVENT_NAME", default="impeachment")

class LocalStorageService:
    """
    Must have same methods and params as the remote version - see append_topics() and append_tweets() in BigQueryService
    """

    def __init__(self, local_dirpath=None, event_name=EVENT_NAME):
        self.event_name = event_name
        self.local_dirpath = local_dirpath or os.path.join(DATA_DIR, "tweet_collection_v2", self.event_name)
        self.topics_csv_filepath = os.path.join(self.local_dirpath, "topics.csv")
        self.tweets_csv_filepath = os.path.join(self.local_dirpath, "tweets.csv")

        print("--------------------")
        print("LOCAL CSV STORAGE...")
        print("  DIR:", os.path.abspath(self.local_dirpath))
        print("  TOPICS CSV:", os.path.abspath(self.topics_csv_filepath))
        print("  TWEETS CSV:", os.path.abspath(self.tweets_csv_filepath))

        #seek_confirmation()
        #if not os.path.isdir(local_dirpath):
        #    os.makedirs(local_dirpath)
        # there should already be a topics.csv existing there...

    def fetch_topic_names(self):
        """Returns a list of topic strings"""
        topics_df = read_csv(self.topics_csv_filepath)
        return topics_df["topic"].tolist()

    def append_topics(self, topics):
        """
        Param: topics (list of str) like ['topic1', 'topic 2']
        """
        new_df = DataFrame(topics, columns=["topic"])

        csv_filepath = self.topics_csv_filepath
        if os.path.isfile(csv_filepath):
            existing_df = read_csv(csv_filepath)
            merged_df = concat([existing_df, new_df])
            merged_df.drop_duplicates(subset=["topic"], inplace=True, keep="first")
            merged_df.to_csv(csv_filepath, index=False)
        else:
            new_df.to_csv(csv_filepath, index=False)

    def append_tweets(self, tweets):
        """
        Param: tweets (list of dict)
        """
        new_df = DataFrame(tweets, columns=[
            'status_id', 'status_text', 'truncated',
            'retweet_status_id', 'reply_status_id', 'reply_user_id',
            'is_quote', 'geo', 'created_at',
            'user_id', 'user_name', 'user_screen_name', 'user_description',
            'user_location', 'user_verified', 'user_created_at'
        ])

        csv_filepath = self.tweets_csv_filepath
        if os.path.isfile(csv_filepath):
            new_df.to_csv(csv_filepath, mode="a", header=False, index=False)
        else:
            new_df.to_csv(csv_filepath, index=False)
