
import pytest
from networkx import DiGraph

@pytest.fixture(scope="module")
def example_graph():
    user_friends = [
        {"screen_name":"A", "friend_names":["B", "C", "D"]},
        {"screen_name":"B", "friend_names":["C", "D"]},
        {"screen_name":"C", "friend_names":["D"]},
        {"screen_name":"D", "friend_names":["C"]},
        {"screen_name":"E", "friend_names":["F"]}
    ]
    graph = DiGraph()
    for row in user_friends:
        user = row["screen_name"]
        friends = row["friend_names"]
        graph.add_node(user)
        graph.add_nodes_from(friends)
        graph.add_edges_from([(user, friend) for friend in friends])
    return graph
