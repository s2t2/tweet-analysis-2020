

from app.retweet_graphs_v2.storage import GraphStorageService

def test_remote_directory_compilation():

    #gcs_dirpath = "storage/data/graphs/2020-08-02-1818"
    ##local_dirpath = "/Users/USERNAME/path/to/repo/data/graphs/2020-08-02-1818"
    ##assert GraphStorageService.compile_gcs_dirpath(local_dirpath) == gcs_dirpath
    #local_dirpath = "data/graphs/2020-08-02-1818"
    #assert GraphStorageService.compile_gcs_dirpath(local_dirpath) == gcs_dirpath

    storage = GraphStorageService()
    assert storage.gcs_dirpath == "storage/data/graphs/example"

    storage = GraphStorageService(local_dirpath="data/graphs/abc123")
    assert storage.gcs_dirpath == "storage/data/graphs/abc123"
