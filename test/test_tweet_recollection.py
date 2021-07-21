
from app.tweet_recollection.collector import TweetCollector

def my_func():

    tc = TweetCollector()

    assert tc.fetch_all_statuses() == [
        {},
        {},
        {},
    ]
