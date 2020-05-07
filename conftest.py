
import pytest
from networkx import DiGraph

@pytest.fixture(scope="module")
def mock_user_friends():
    return [
        {"screen_name":"A", "friend_names":["B", "C", "D"]},
        {"screen_name":"B", "friend_names":["C", "D"]},
        {"screen_name":"C", "friend_names":["D"]},
        {"screen_name":"D", "friend_names":["C"]},
        {"screen_name":"E", "friend_names":["F"]},
    ]

@pytest.fixture(scope="module")
def mock_graph(mock_user_friends):
    graph = DiGraph()
    for row in mock_user_friends:
        user = row["screen_name"]
        friends = row["friend_names"]
        graph.add_node(user)
        graph.add_nodes_from(friends)
        graph.add_edges_from([(user, friend) for friend in friends])
    return graph

@pytest.fixture(scope="module")
def expected_nodes():
    return ["A", "B", "C", "D", "E", "F"] # all users, followed or following

@pytest.fixture(scope="module")
def expected_edges():
    return [
        ("A", "B"), ("A", "C"), ("A", "D"), # "A" follows "B", "C", and "D"
        ("B", "C"), ("B", "D"), # "B" follows "C" and "D"
        ("C", "D"), # "C" follows "D"
        ("D", "C"), # "D" follows "C"
        ("E", "F") # "E" follows "F" and "F" follows no-one
    ]
