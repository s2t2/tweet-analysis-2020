
import os
from pprint import pprint
from time import sleep

from dotenv import load_dotenv
from tweepy.streaming import StreamListener
from tweepy import Stream
from urllib3.exceptions import ProtocolError

from app import seek_confirmation
from app.twitter_service import TwitterService
from app.bq_service import BigQueryService, generate_timestamp
from app.tweet_collection_v2.csv_storage import LocalStorageService
from app.tweet_collection_v2.tweet_parser import parse_status

load_dotenv()

STORAGE_ENV = os.getenv("STORAGE_ENV", default="local") # "local" OR "remote"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="20"))

class TopicResetEvent(Exception):
    pass

class TweetCollector(StreamListener):

    def __init__(self, twitter_service=None, storage_env=STORAGE_ENV, bq_service=None, csv_service=None, batch_size=BATCH_SIZE):
        self.twitter_service = twitter_service or TwitterService()
        self.api = self.twitter_service.api
        self.auth = self.api.auth
        self.parse_status = parse_status

        self.storage_env = storage_env
        if self.storage_env == "local":
            self.storage_service = csv_service or LocalStorageService()
        elif self.storage_env == "remote":
            self.storage_service = bq_service or BigQueryService()
        else:
            raise ValueError("Expecting the STORAGE_ENV to be 'local' or 'remote'. Please try again...")

        self.batch_size = batch_size
        self.batch = []
        self.counter = 0

        print("-------------------------------")
        print("STREAM LISTENER...")
        print("  STORAGE ENV:", self.storage_env.upper())
        print("  STORAGE SERVICE:", type(self.storage_service))
        print("  BATCH SIZE:", self.batch_size)
        print("--------------------------------")


    def set_topics(self):
        self.topics = self.storage_service.fetch_topic_names()
        print("SET TOPICS:", self.topics)

    def reset_topics(self):
        self.set_topics()
        raise TopicResetEvent("Let's trigger the listener to re-start in a kind of hacky way :-D")

    #
    # CONNECT AND LISTEN FOR TWEETS
    #

    def on_connect(self):
        print("LISTENER IS CONNECTED!")

    def on_status(self, status):
        """Param status (tweepy.models.Status)"""
        if self.is_collectable(status):
            self.counter +=1
            print("----------------")
            print(f"DETECTED AN INCOMING TWEET! ({self.counter} -- {status.id_str})")
            self.collect_in_batches(status)

    #
    # COLLECT SPECIFIED TWEETS
    #

    @staticmethod
    def is_collectable(status):
        """Param status (tweepy.models.Status)"""
        return (status.lang == "en"
                #and status.user.verified
                #and status.in_reply_to_status_id == None
                #and status.in_reply_to_user_id == None
                #and status.in_reply_to_screen_name == None
                #and status.is_quote_status == False
                #and status.retweeted == False
                #and not hasattr(status, "retweeted_status")
        )

    def collect_in_batches(self, status):
        """
        Param status (tweepy.models.Status)
        Moving this logic out of on_status in hopes of preventing ProtocolErrors
        Storing in batches to reduce API calls, and in hopes of preventing ProtocolErrors
        """
        self.batch.append(self.parse_status(status))
        if len(self.batch) >= self.batch_size:
            self.store_and_clear_batch()

    def store_and_clear_batch(self):
        print("STORING BATCH OF", len(self.batch), "TWEETS...")
        self.storage_service.append_tweets(self.batch)
        print("CLEARING BATCH...")
        self.batch = []
        self.counter = 0

    #
    # HANDLE ERRORS
    #

    def on_exception(self, exception):
        # has encountered errors:
        #  + urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(0 bytes read)'
        #  + urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool
        print("EXCEPTION:", type(exception))
        print(exception)

    def on_error(self, status_code):
        print("ERROR:", status_code)

    def on_limit(self, track):
        """Param: track (int) starts low and subsequently increases"""
        print("RATE LIMITING", track)
        sleep_seconds = self.backoff_strategy(track)
        print("SLEEPING FOR:", sleep_seconds, "SECONDS...")
        sleep(sleep_seconds)

    @staticmethod
    def backoff_strategy(i):
        """
        Param: i (int) increasing rate limit number from the twitter api
        Returns: number of seconds to sleep for
        """
        return (int(i) + 1) ** 2 # raise to the power of two

    def on_timeout(self):
        print("TIMEOUT!")
        return True # don't kill the stream!

    def on_warning(self, notice):
        print("DISCONNECTION WARNING:", type(notice))
        print(notice)

    def on_disconnect(self, notice):
        print("DISCONNECT:", type(notice))

if __name__ == "__main__":

    listener = TweetCollector()
    seek_confirmation()
    listener.set_topics()

    stream = Stream(listener.auth, listener)
    print("STREAM", type(stream))

    while True:
        try:
            stream.filter(track=listener.topics)
        except ProtocolError:
            print("--------------------------------")
            print("RESTARTING AFTER PROTOCOL ERROR!")
            continue
        except TopicResetEvent as event:
            print("--------------------------------")
            print("RESTARTING AFTER TOPICS REFRESH!")
            continue

    # this never gets reached
