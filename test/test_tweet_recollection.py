
from app.tweet_recollection.collector import Collector

def test_recollection():

    collector = Collector()

    #assert collector.limit == 100000
    #assert collector.batch_size == 100
    assert collector.batch_size <= 100
    assert collector.batch_size <= collector.limit

    methods = list(dir(collector))
    assert "perform" in methods
    assert "fetch_remaining_status_ids" in methods
    assert "lookup_statuses" in methods
    assert "save_statuses" in methods
    assert "save_urls" in methods
