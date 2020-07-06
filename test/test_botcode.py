
from networkx import DiGraph

from app.botcode import (ALPHA, LAMBDA_1, LAMBDA_2, EPSILON,
                        compute_link_energy, compile_energy_graph, parse_bidirectional_links)
from conftest import compile_mock_rt_graph

def test_default_hyperparams():
    # should match the default values described in the botcode README file
    assert ALPHA == [1.0, 100.0, 100.0]
    assert LAMBDA_1 == 0.8
    assert LAMBDA_2 == 0.6
    assert EPSILON == 0.001

def test_mock_rt_graph(mock_rt_graph):
    in_degrees = dict(mock_rt_graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(mock_rt_graph.out_degree(weight="rt_count")) # users doing the retweeting
    assert in_degrees == {'user1': 0, 'leader1': 100.0, 'user2': 0, 'user3': 0, 'leader2': 60.0, 'user4': 0, 'user5': 0, 'leader3': 40.0, 'colead1': 20.0, 'colead2': 30.0, 'colead3': 40.0, 'colead4': 10.0}
    assert out_degrees == {'user1': 40.0, 'leader1': 0, 'user2': 60.0, 'user3': 40.0, 'leader2': 0, 'user4': 20.0, 'user5': 40.0, 'leader3': 0, 'colead1': 30.0, 'colead2': 20.0, 'colead3': 10.0, 'colead4': 40.0}

def test_link_energy_nonactivation():
    #
    # setup
    #
    graph = compile_mock_rt_graph([
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
    ])
    in_degrees = dict(graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(graph.out_degree(weight="rt_count")) # users doing the retweeting
    assert in_degrees == {'user1': 0, 'leader1': 10.0, 'user2': 0, 'user3': 0, 'leader2': 6.0, 'user4': 0, 'user5': 0, 'leader3': 4.0, 'colead1': 2.0, 'colead2': 3.0, 'colead3': 4.0, 'colead4': 1.0}
    assert out_degrees == {'user1': 4.0, 'leader1': 0, 'user2': 6.0, 'user3': 4.0, 'leader2': 0, 'user4': 2.0, 'user5': 4.0, 'leader3': 0, 'colead1': 3.0, 'colead2': 2.0, 'colead3': 1.0, 'colead4': 4.0}

    #
    # w/o sufficient number of retweets, given default hyperparams, not enough to activate, energy is zero
    #
    energy = compute_link_energy('colead1', 'colead2', 3.0, in_degrees, out_degrees, alpha=[1,100,100])
    assert energy == [0.0, 0.0, 0.0, 0.0]
    assert sum(energy) == 0

    #
    # w/ sufficient number of retweets, given different hyperparams, energy is positive
    #
    energy = compute_link_energy('colead1', 'colead2', 3.0, in_degrees, out_degrees, alpha=[1,10,10])
    assert energy == [0.01676872682112003, 0.027947878035200054, 0.01120709909211522, 0.022358302428160046]
    assert sum(energy) > 0

def test_link_energy(mock_rt_graph):
    #
    # w/ sufficient number of retweets, given default hyperparams, energy is positive
    #
    in_degrees = dict(mock_rt_graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(mock_rt_graph.out_degree(weight="rt_count")) # users doing the retweeting
    energy = compute_link_energy('colead1', 'colead2', 30.0, in_degrees, out_degrees, alpha=[1,100,100])
    assert energy == [0.16768726821120034, 0.2794787803520006, 0.1120709909211522, 0.22358302428160048]
    assert sum(energy) > 0

def test_energy_grapher(mock_rt_graph):

    #
    # setup and inspection
    #

    assert list(mock_rt_graph.edges(data=True)) == [
        ('user1', 'leader1', {'rt_count': 40.0}),
        ('user2', 'leader1', {'rt_count': 60.0}),
        ('user3', 'leader2', {'rt_count': 40.0}),
        ('user4', 'leader2', {'rt_count': 20.0}),
        ('user5', 'leader3', {'rt_count': 40.0}),
        ('colead1', 'colead2', {'rt_count': 30.0}),
        ('colead2', 'colead1', {'rt_count': 20.0}),
        ('colead3', 'colead4', {'rt_count': 10.0}),
        ('colead4', 'colead3', {'rt_count': 40.0})
    ]
    assert sorted(list(mock_rt_graph.nodes)) == [
        'colead1', 'colead2', 'colead3', 'colead4',
        'leader1', 'leader2', 'leader3',
        'user1', 'user2', 'user3', 'user4', 'user5'
    ]

    prior_probabilities = dict.fromkeys(list(mock_rt_graph.nodes), 0.5)
    assert prior_probabilities == {
        'user1': 0.5, 'leader1': 0.5, 'user2': 0.5, 'user3': 0.5,
        'leader2': 0.5, 'user4': 0.5, 'user5': 0.5, 'leader3': 0.5,
        'colead1': 0.5, 'colead2': 0.5, 'colead3': 0.5, 'colead4': 0.5
    }

    in_degrees = dict(mock_rt_graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(mock_rt_graph.out_degree(weight="rt_count")) # users doing the retweeting
    assert in_degrees == {
        'user1': 0, 'leader1': 100.0, 'user2': 0, 'user3': 0,
        'leader2': 60.0, 'user4': 0, 'user5': 0, 'leader3': 40.0,
        'colead1': 20.0, 'colead2': 30.0, 'colead3': 40.0, 'colead4': 10.0
    }
    assert out_degrees == {
        'user1': 40.0, 'leader1': 0, 'user2': 60.0, 'user3': 40.0,
        'leader2': 0, 'user4': 20.0, 'user5': 40.0, 'leader3': 0,
        'colead1': 30.0, 'colead2': 20.0, 'colead3': 10.0, 'colead4': 40.0
    }

    links = parse_bidirectional_links(mock_rt_graph)
    assert links == [
        ['user1', 'leader1', True, False, 40.0, 0],
        ['user2', 'leader1', True, False, 60.0, 0],
        ['user3', 'leader2', True, False, 40.0, 0],
        ['user4', 'leader2', True, False, 20.0, 0],
        ['user5', 'leader3', True, False, 40.0, 0],
        ['colead1', 'colead2', True, True, 30.0, 20.0],
        ['colead2', 'colead1', True, True, 20.0, 30.0],
        ['colead3', 'colead4', True, True, 10.0, 40.0],
        ['colead4', 'colead3', True, True, 40.0, 10.0]
    ] # represents the number of times each pair of users has retweeted eachother

    energies = [(link[0], link[1], compute_link_energy(link[0], link[1], link[4], in_degrees, out_degrees)) for link in links]
    assert energies == [
        ('user1', 'leader1', [4.378212571352552, 7.297020952254254, 2.926105401853955, 5.837616761803403]),
        ('user2', 'leader1', [12.212770724430582, 20.35461787405097, 8.162201767494437, 16.283694299240775]),
        ('user3', 'leader2', [2.466816598014041, 4.111360996690069, 1.6486557596727172, 3.289088797352055]),
        ('user4', 'leader2', [0.11179151214080021, 0.1863191869013337, 0.0747139939474348, 0.14905534952106697]),
        ('user5', 'leader3', [1.1382209562616026, 1.8970349271026712, 0.760711005768171, 1.517627941682137]),
        ('colead1', 'colead2', [0.16768726821120034, 0.2794787803520006, 0.1120709909211522, 0.22358302428160048]),
        ('colead2', 'colead1', [0.004024201565597737, 0.006707002609329562, 0.0026895080463411537, 0.00536560208746365]),
        ('colead3', 'colead4', [0.0, 0, 0.0, 0.0]), # number of retweets not sufficient to activate the energy function
        ('colead4', 'colead3', [1.1382209562616026, 1.8970349271026712, 0.760711005768171, 1.517627941682137])
    ] # people doing the retweeting

    positive_energies = [e for e in energies if sum(e[2]) > 0]
    assert positive_energies == [
        ('user1', 'leader1', [4.378212571352552, 7.297020952254254, 2.926105401853955, 5.837616761803403]),
        ('user2','leader1', [12.212770724430582, 20.35461787405097, 8.162201767494437, 16.283694299240775]),
        ('user3','leader2', [2.466816598014041, 4.111360996690069, 1.6486557596727172, 3.289088797352055]),
        ('user4', 'leader2', [0.11179151214080021, 0.1863191869013337, 0.0747139939474348, 0.14905534952106697]),
        ('user5', 'leader3', [1.1382209562616026, 1.8970349271026712, 0.760711005768171, 1.517627941682137]),
        ('colead1', 'colead2', [0.16768726821120034, 0.2794787803520006, 0.1120709909211522, 0.22358302428160048]),
        ('colead2', 'colead1',[0.004024201565597737, 0.006707002609329562, 0.0026895080463411537, 0.00536560208746365]),
        ('colead4', 'colead3', [1.1382209562616026, 1.8970349271026712, 0.760711005768171, 1.517627941682137])
    ] # people doing the most retweeting

    #
    # it produces an energy graph and other important results:
    #

    energy_graph, pl, user_data = compile_energy_graph(mock_rt_graph, prior_probabilities,
                                                        positive_energies, out_degrees, in_degrees)

    assert isinstance(energy_graph, DiGraph)
    assert list(energy_graph.nodes) == [
        'user1', 'leader1', 'user2', 'user3', 'leader2', 'user4', 'user5', 'leader3',
        'colead1', 'colead2', 'colead4', 'colead3', 0, 1
    ] # includes all original graph nodes, as well as 0 and 1 (though not immediately clear why)
    assert list(energy_graph.edges(data=True)) == [
        ('user1', 'leader1', {'capacity': 0.0036485104761272424}),
        ('user1', 0, {'capacity': 2.519226673861572}),
        ('leader1', 'user1', {'capacity': 0.0036485104761272424}),
        ('leader1', 'user2', {'capacity': 0.010177308937025842}),
        ('leader1', 0, {'capacity': 15.894635625321241}),
        ('user2', 'leader1', {'capacity': 0.010177308937025842}),
        ('user2', 0, {'capacity': 5.7868903035412}),
        ('user3', 'leader2', {'capacity': 0.002055680498344925}),
        ('user3', 0, {'capacity': 1.7220152699816351}),
        ('leader2', 'user3', {'capacity': 0.002055680498344925}),
        ('leader2', 'user4', {'capacity': 9.315959345064517e-05}),
        ('leader2', 0, {'capacity': 3.055796861489319}),
        ('user4', 'leader2', {'capacity': 9.315959345064517e-05}),
        ('user4', 0, {'capacity': 0.7397735570820041}),
        ('user5', 'leader3', {'capacity': 0.0009485174635512905}),
        ('user5', 0, {'capacity': 1.1678801710673887}),
        ('leader3', 'user5', {'capacity': 0.0009485174635512905}),
        ('leader3', 0, {'capacity': 1.736042131734639}),
        ('colead1', 'colead2', {'capacity': 0.00014309289148063935}),
        ('colead1', 0, {'capacity': 0.7667739200275123}),
        ('colead2', 'colead1', {'capacity': 0.00014309289148063935}),
        ('colead2', 0, {'capacity': 0.8484690674614424}),
        ('colead4', 'colead3', {'capacity': 0.0009485174635512905}),
        ('colead4', 0, {'capacity': 1.1678801710673887}),
        ('colead3', 'colead4', {'capacity': 0.0009485174635512905}),
        ('colead3', 0, {'capacity': 1.736042131734639}),
        (1, 'user1', {'capacity': 3.974982353836296}),
        (1, 'leader1', {'capacity': 4.847805914212305}),
        (1, 'user2', {'capacity': 9.84763656941437}),
        (1, 'user3', {'capacity': 2.5422317888213035}),
        (1, 'leader2', {'capacity': 1.3388736281445532}),
        (1, 'user4', {'capacity': 0.7769442348688201}),
        (1, 'user5', {'capacity': 1.5463386390243716}),
        (1, 'leader3', {'capacity': 0.9781766783571215}),
        (1, 'colead1', {'capacity': 0.8198504891653093}),
        (1, 'colead2', {'capacity': 0.7381553417313793}),
        (1, 'colead3', {'capacity': 0.9781766783571215}),
        (1, 'colead4', {'capacity': 1.5463386390243716})
    ] # what's up with the extra 0s and 1s in here? for baseline comparisons? also, capacity for what?

    assert sorted(pl) == ['colead1', 'colead4', 'user1', 'user2', 'user3', 'user4', 'user5'] # seems to represent the users who retweet but don't get retweeted (a.k.a the bot list)

    assert user_data == {
        'user1': {'user_id': 'user1', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'leader1': {'user_id': 'leader1', 'out': 0, 'in': 100.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user2': {'user_id': 'user2', 'out': 60.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user3': {'user_id': 'user3', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'leader2': {'user_id': 'leader2', 'out': 0, 'in': 60.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user4': {'user_id': 'user4', 'out': 20.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user5': {'user_id': 'user5', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'leader3': {'user_id': 'leader3', 'out': 0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead1': {'user_id': 'colead1', 'out': 30.0, 'in': 20.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead2': {'user_id': 'colead2', 'out': 20.0, 'in': 30.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead3': {'user_id': 'colead3', 'out': 10.0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead4': {'user_id': 'colead4', 'out': 40.0, 'in': 10.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0}
    }

def test_bot_probabilities(mock_rt_graph):

    #
    # setup
    #

    in_degrees = dict(mock_rt_graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(mock_rt_graph.out_degree(weight="rt_count")) # users doing the retweeting

    links = parse_bidirectional_links(mock_rt_graph)
    energies = [(link[0], link[1], compute_link_energy(link[0], link[1], link[4], in_degrees, out_degrees)) for link in links]
    positive_energies = [e for e in energies if sum(e[2]) > 0]

    prior_probabilities = dict.fromkeys(list(mock_rt_graph.nodes), 0.5)
    energy_graph, pl, user_data = compile_energy_graph(mock_rt_graph, prior_probabilities, positive_energies, out_degrees, in_degrees)

    #
    # it assigns bot probabilities to 1 if user is in bot list returned from energy grapher function
    #

    bot_probabilities = dict.fromkeys(list(user_data.keys()), 0) # start with defaults of 0 for each user
    for user in pl:
        user_data[user]["clustering"] = 1
        bot_probabilities[user] = 1

    assert bot_probabilities == {
        'colead1': 1, 'colead2': 0, 'colead3': 0, 'colead4': 1,
        'leader1': 0, 'leader2': 0, 'leader3': 0,
        'user1': 1, 'user2': 1, 'user3': 1, 'user4': 1, 'user5': 1
    }

    assert user_data == {
        'user1': {'user_id': 'user1', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'leader1': {'user_id': 'leader1', 'out': 0, 'in': 100.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user2': {'user_id': 'user2', 'out': 60.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'user3': {'user_id': 'user3', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'leader2': {'user_id': 'leader2', 'out': 0, 'in': 60.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'user4': {'user_id': 'user4', 'out': 20.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'user5': {'user_id': 'user5', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'leader3': {'user_id': 'leader3', 'out': 0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead1': {'user_id': 'colead1', 'out': 30.0, 'in': 20.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1},
        'colead2': {'user_id': 'colead2', 'out': 20.0, 'in': 30.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead3': {'user_id': 'colead3', 'out': 10.0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
        'colead4': {'user_id': 'colead4', 'out': 40.0, 'in': 10.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 1}
     }
