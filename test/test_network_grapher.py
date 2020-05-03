import os
from networkx import read_gpickle

from app.workers.network_grapher_2 import NetworkGrapher
from app.storage_service import BigQueryService

def test_network_grapher(example_graph):
    expected_nodes = ['A', 'B', 'C', 'D', 'E', 'F']
    expected_edges = [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'C'), ('E', 'F')]

    graph_filepath = os.path.join(os.path.dirname(__file__), "data", "example_graph.gpickle")
    if os.path.isfile(graph_filepath): os.remove(graph_filepath)
    assert os.path.isfile(graph_filepath) == False

    bq_service = BigQueryService()
    grapher = NetworkGrapher(graph=example_graph, bq=bq_service)
    # initializing with the completed graph allows us to the skip / mock the performance
    assert list(grapher.graph.nodes) == expected_nodes
    assert list(grapher.graph.edges) == expected_edges

    grapher.write_to_file(graph_filepath)
    assert os.path.isfile(graph_filepath) == True

    reconstituted_graph = read_gpickle(graph_filepath)
    assert list(reconstituted_graph.nodes) == expected_nodes
    assert list(reconstituted_graph.edges) == expected_edges
