
from networkx import DiGraph

from app.botcode import compute_link_energy, ALPHA, LAMBDA_1, LAMBDA_2, EPSILON

def test_hyperparams():
    # should match the default values described in the botcode README file
    assert ALPHA == [1.0, 100.0, 100.0]
    assert LAMBDA_1 == 0.8
    assert LAMBDA_2 == 0.6
    assert EPSILON == 0.001

def compile_mock_rt_graph(edge_list):
    """
    Param edge_list (list of dict) like:
        [
            {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "retweet_count": 4},
            {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "retweet_count": 6},
            {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "retweet_count": 4},
        ]
    """
    graph = DiGraph()
    for row in edge_list:
        graph.add_edge(row["user_screen_name"], row["retweet_user_screen_name"], rt_count=float(row["retweet_count"]))
    return graph

def test_sigmoid_activation():

    #
    # CASE A
    #
    # if there aren't a sufficient number of retweets, given the hyperparams,
    # ... the function shouldn't activate
    # ... and the energies shouldn't be positive
    #

    mock_edges = [
        # add some examples of users retweeting others:
        {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "retweet_count": 4},
        {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "retweet_count": 6},
        {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "retweet_count": 4},
        {"user_screen_name": "user4", "retweet_user_screen_name": "leader2", "retweet_count": 2},
        {"user_screen_name": "user5", "retweet_user_screen_name": "leader3", "retweet_count": 4},
        # add some examples of users retweeting eachother:
        {"user_screen_name": "colead1", "retweet_user_screen_name": "colead2", "retweet_count": 3},
        {"user_screen_name": "colead2", "retweet_user_screen_name": "colead1", "retweet_count": 2},
        {"user_screen_name": "colead3", "retweet_user_screen_name": "colead4", "retweet_count": 1},
        {"user_screen_name": "colead4", "retweet_user_screen_name": "colead3", "retweet_count": 4}
    ]
    graph = compile_mock_rt_graph(mock_edges)
    in_degrees = dict(graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(graph.out_degree(weight="rt_count")) # users doing the retweeting
    assert in_degrees == {'user1': 0, 'leader1': 10.0, 'user2': 0, 'user3': 0, 'leader2': 6.0, 'user4': 0, 'user5': 0, 'leader3': 4.0, 'colead1': 2.0, 'colead2': 3.0, 'colead3': 4.0, 'colead4': 1.0}
    assert out_degrees == {'user1': 4.0, 'leader1': 0, 'user2': 6.0, 'user3': 4.0, 'leader2': 0, 'user4': 2.0, 'user5': 4.0, 'leader3': 0, 'colead1': 3.0, 'colead2': 2.0, 'colead3': 1.0, 'colead4': 4.0}

    energy = compute_link_energy('colead1', 'colead2', 3.0, in_degrees, out_degrees, alpha=[1,100,100])
    assert energy == [0.0, 0.0, 0.0, 0.0]
    assert sum(energy) == 0

    #
    # CASE B
    #
    # if there are a sufficient number of retweets, given the hyperparams,
    # ... the function should activate
    # ... and the energies should be positive
    #

    # Case B-1: lowering the hyperparams to suit the dataset
    energy_b1 = compute_link_energy('colead1', 'colead2', 3.0, in_degrees, out_degrees, alpha=[1,10,10])
    assert energy_b1 == [0.01676872682112003, 0.027947878035200054, 0.01120709909211522, 0.022358302428160046]
    assert sum(energy_b1) > 0

    # Case B-2: adapting the dataset to suit the default hyperparams
    mock_edges = [
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
    graph = compile_mock_rt_graph(mock_edges)
    in_degrees = dict(graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(graph.out_degree(weight="rt_count")) # users doing the retweeting
    assert in_degrees == {'user1': 0, 'leader1': 100.0, 'user2': 0, 'user3': 0, 'leader2': 60.0, 'user4': 0, 'user5': 0, 'leader3': 40.0, 'colead1': 20.0, 'colead2': 30.0, 'colead3': 40.0, 'colead4': 10.0}
    assert out_degrees == {'user1': 40.0, 'leader1': 0, 'user2': 60.0, 'user3': 40.0, 'leader2': 0, 'user4': 20.0, 'user5': 40.0, 'leader3': 0, 'colead1': 30.0, 'colead2': 20.0, 'colead3': 10.0, 'colead4': 40.0}

    energy_b2 = compute_link_energy('colead1', 'colead2', 30.0, in_degrees, out_degrees, alpha=[1,100,100])
    assert energy_b2 == [0.16768726821120034, 0.2794787803520006, 0.1120709909211522, 0.22358302428160048]
    assert sum(energy_b2) > 0
