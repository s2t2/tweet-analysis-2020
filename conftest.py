import os

import pytest
from networkx import DiGraph

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test", "data")
TMP_DATA_DIR = os.path.join(TEST_DATA_DIR, "tmp")

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

mock_rt_graph_edge_list = [
    # add some examples of users retweeting others:
    {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "retweet_count": 40},
    {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "retweet_count": 60},
    {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "retweet_count": 40},
    {"user_screen_name": "user4", "retweet_user_screen_name": "leader2", "retweet_count": 20},
    {"user_screen_name": "user5", "retweet_user_screen_name": "leader3", "retweet_count": 40},
    # add some examples of users retweeting eachother:
    {"user_screen_name": "colead1", "retweet_user_screen_name": "colead2", "retweet_count": 30},
    {"user_screen_name": "colead2", "retweet_user_screen_name": "colead1", "retweet_count": 20},
    {"user_screen_name": "colead3", "retweet_user_screen_name": "colead4", "retweet_count": 10},
    {"user_screen_name": "colead4", "retweet_user_screen_name": "colead3", "retweet_count": 40}
]

def compile_mock_rt_graph(edge_list=mock_rt_graph_edge_list, weight_attr="retweet_count"):
    """
    Param
        edge_list (list of dict) like: [
            {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "weight": 4},
            {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "weight": 6},
            {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "weight": 4},
        ]

        weight_attr (str) the name of the weight attribute for each edge in the edge list
    """
    graph = DiGraph()
    for row in edge_list:
        graph.add_edge(row["user_screen_name"], row["retweet_user_screen_name"], rt_count=float(row[weight_attr]))
    return graph

@pytest.fixture(scope="module")
def mock_rt_graph():
    """
    Returns a retweet graph with sufficient energy to populate bot probabilities given default hyperparams
    """
    return compile_mock_rt_graph()
