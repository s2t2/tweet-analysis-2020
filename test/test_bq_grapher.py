import os
from networkx import read_gpickle

from app.workers.bq_grapher import BigQueryGrapher
from app.bq_service import BigQueryService

def test_network_grapher(mock_graph, expected_nodes, expected_edges):

    graph_filepath = os.path.join(os.path.dirname(__file__), "data", "mock_graph.gpickle")
    if os.path.isfile(graph_filepath): os.remove(graph_filepath)
    assert os.path.isfile(graph_filepath) == False

    grapher = BigQueryGrapher(bq_service=BigQueryService()) # TODO: mock grapher.perform() method to return the graph, instead of initializing with it
    grapher.graph = mock_graph
    assert list(grapher.graph.nodes) == expected_nodes
    assert list(grapher.graph.edges) == expected_edges

    grapher.write_graph_to_file(graph_filepath)
    assert os.path.isfile(graph_filepath) == True

    reconstituted_graph = read_gpickle(graph_filepath)
    assert list(reconstituted_graph.nodes) == expected_nodes
    assert list(reconstituted_graph.edges) == expected_edges
