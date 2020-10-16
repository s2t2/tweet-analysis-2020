



from app.tweet_collection_v2.stream_listener import TweetCollector

def test_backoff_strategy():

    collector = TweetCollector()

    #assert collector.backoff_strategy(1) == 4
    #assert collector.backoff_strategy(10) == 121
    #assert collector.backoff_strategy(100) == 10201
    #assert collector.backoff_strategy(1000) == 1002001
    #assert collector.backoff_strategy(10000) == 100020001

    assert collector.backoff_strategy(1) == 3
    assert collector.backoff_strategy(10) == 30
    assert collector.backoff_strategy(100) == 300
    assert collector.backoff_strategy(1000) == 3000
    assert collector.backoff_strategy(10000) == 30000
