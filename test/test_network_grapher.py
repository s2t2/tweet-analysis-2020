import os
import pandas
from networkx import DiGraph, Graph

from app.workers.network_grapher import compile_nodes_and_edges, generate_graph

MOCK_CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "data", "mock_network.csv")

def test_nodes_and_edges():
    #
    # Given:
    #     A doesn't follow anyone
    #     B follows A
    #     C follows B and A
    #     D and E follow eachother
    #
    df = pandas.read_csv(MOCK_CSV_FILEPATH, header=None)
    screen_names = df[0].tolist()

    nodes, edges = compile_nodes_and_edges(screen_names, csv_filepath=MOCK_CSV_FILEPATH)
    assert nodes == {'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1}
    assert edges == [('A', 'B'), ('B', 'C'), ('A', 'C'), ('E', 'D'), ('D', 'E')]

def test_graph_generation():
    graph = generate_graph([('A', 'B'), ('B', 'C'), ('A', 'C'), ('E', 'D'), ('D', 'E')])
    assert isinstance(graph, DiGraph)
    assert len(graph.edges) == 5
    assert len(graph.nodes) == 5

def test_undirected():
    # https://networkx.github.io/documentation/latest/reference/classes/generated/networkx.DiGraph.to_undirected.html#networkx.DiGraph.to_undirected
    graph = generate_graph([('A', 'B'), ('B', 'A')])
    undirected = graph.to_undirected()
    assert isinstance(graph, DiGraph) and isinstance(undirected, Graph)
    assert len(graph.nodes) == 2 and len(undirected.nodes) == 2
    assert len(graph.edges) == 2 and len(undirected.edges) == 1
