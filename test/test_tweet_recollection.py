
from app.tweet_recollection.collector import Collector

def test_recollection():

    collector = Collector()

    #assert collector.limit == 100000
    #assert collector.batch_size == 100
    assert collector.batch_size <= collector.limit

    assert "perform" in list(dir(collector))
