import os
from networkx import read_gpickle

from app.workers.pg_grapher import NetworkGrapher
from app.storage_service import BigQueryService

def test_performance():

    graph_filepath = os.path.join(os.path.dirname(__file__), "data", "pg_graph.gpickle")
    if os.path.isfile(graph_filepath): os.remove(graph_filepath)
    assert os.path.isfile(graph_filepath) == False

    grapher = NetworkGrapher(table_name="user_friends_10k", dry_run=True) # need to setup this table locally before testing. SEE NOTES.md
    assert len(grapher.graph.nodes) == 0
    assert len(grapher.graph.edges) == 0

    grapher.perform()
    assert len(grapher.graph.nodes) == 2_559_553
    assert len(grapher.graph.edges) == 5_438_049

    #grapher.write_to_file(graph_filepath)
    #assert os.path.isfile(graph_filepath) == True

    #reconstituted_graph = read_gpickle(graph_filepath)
    #assert list(reconstituted_graph.nodes) == expected_nodes
    #assert list(reconstituted_graph.edges) == expected_edges
