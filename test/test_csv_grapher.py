import os
import pandas
from networkx import DiGraph, Graph

# columns: screen_name, friend_1, friend_2, friend_3, friend_4, etc...
#CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "example_network.csv")
MOCK_CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "data", "mock_network.csv")

def compile_nodes_and_edges(screen_names, csv_filepath=MOCK_CSV_FILEPATH):
    """
    Each edge tuple like... "0 follows 1"
    """
    nodes = {}
    for screen_name in screen_names:
        nodes[screen_name] = 1

    edges = []
    with open(csv_filepath) as csv_file:
        for index, line in enumerate(csv_file):
            #print("-------------")
            user_friends = line.strip("\n").split(",")
            user_name = user_friends[0] # follower
            friend_names = user_friends[1:] # friends
            #print("USER:", user_name, "FRIENDS:", friend_names)

            for friend_name in friend_names:
                if friend_name in nodes.keys():
                    #edges.append((friend_name, user_name)) # 0 is followed by 1
                    edges.append((user_name, friend_name)) # 0 follows 1

    return nodes, edges

def generate_graph(edges):
    """
    Converts edges into a networkx digraph object.

    Param edges (list of tuples)
        ... like [('A', 'B'), ('B', 'C'), ('A', 'C'), ('E', 'D'), ('D', 'E')]
        ... where 'B' follows 'A', 'C' follows 'B', etc.

    Returns graph (networkx.classes.digraph.DiGraph)
    """
    graph = DiGraph()
    for edge in edges:
        source = edge[0] # source, a.k.a friend, a.k.a followed
        recipient = edge[1] # recipient, a.k.a user, a.k.a follower
        graph.add_node(source)
        graph.add_node(recipient)
        graph.add_edge(source, recipient)
    return graph

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
    assert nodes == {'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1, 'F': 1}
    assert edges == [
        ('A', 'B'), ('A', 'C'), ('A', 'D'), # "A" follows "B", "C", and "D"
        ('B', 'C'), ('B', 'D'), # "B" follows "C" and "D"
        ('C', 'D'), # "C" follows "D"
        ('D', 'C'), # "D" follows "C"
        ('E', 'F') # "E" follows "F" and "F" follows no-one
    ]

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

def test_duplication():
    graph = DiGraph()
    graph.add_node("A")
    graph.add_node("A")
    assert len(graph.nodes) == 1
