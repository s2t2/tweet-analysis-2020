

from app.retweet_graphs_v2.storage import GraphStorageService

def test_remote_directory_compilation():

    storage = GraphStorageService()
    assert storage.gcs_dirpath == "storage/data/graphs/example"

    storage = GraphStorageService(local_dirpath="data/graphs/abc123")
    assert storage.gcs_dirpath == "storage/data/graphs/abc123"
