


import os
from pprint import pprint

import numpy as np
from networkx import DiGraph

from app.botcode import parse_bidirectional_links, compute_link_energy, compile_energy_graph

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

if __name__ == "__main__":

    graph = compile_mock_rt_graph([
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
    ])

    print("----------------------")
    in_degrees = dict(graph.in_degree(weight="rt_count")) # users receiving retweets
    out_degrees = dict(graph.out_degree(weight="rt_count")) # users doing the retweeting
    print("IN-DEGREES...")
    pprint(in_degrees)
    print("OUT-DEGREES...")
    pprint(out_degrees)

    print("----------------------")
    print("ENSURING ALL NODES ARE REPRESENTED IN IN-DEGREE AND OUT-DEGREE VIEWS...")
    for node in graph.nodes():
        if node not in in_degrees.keys():
            print("ADDING NODE TO IN-DEGREES")
            in_degrees[node] = 0
        if node not in out_degrees.keys():
            print("ADDING NODE TO OUT-DEGREES")
            out_degrees[node] = 0
    print("IN-DEGREES:", len(in_degrees))
    print("OUT-DEGREES:", len(out_degrees))

    print("----------------------")
    print("GATHERING LINKS...")
    links = parse_bidirectional_links(graph) #
    pprint(links) #> list of links like ['user1', 'leader1', True, False, 4.0, 0]

    print("----------------------")
    print("COMPUTING ENERGIES...")
    energies = [(link[0], link[1], compute_link_energy(link[0], link[1], link[4], in_degrees, out_degrees)) for link in links]
    print(len(energies))
    #pprint(energies) #> list of tuples like... ('user1', 'leader1', [0.0, 0, 0.0, 0.0])

    #print("----------------------")
    positive_energies = [e for e in energies if sum(e[2]) > 0]
    print("POSITIVE ENERGIES...")
    print(len(positive_energies))
    pprint(positive_energies)

    print("----------------------")
    print("STARTING WITH DEFAULT BOT PROBABILITIES (PRIORS)")
    nodes = list(graph.nodes) #> ["user1", "user2", "user3", etc.]
    bot_probabilities = dict.fromkeys(nodes, 0.5) # no priors, set all at 0.5!
    #print(bot_probabilities) #> {'user1': 0.5, 'user2': 0.5, 'user3': 0.5}

    print("----------------------")
    print("CONSTRUCTING RETWEET ENERGY GRAPH...")
    energy_graph, pl, user_data = compile_energy_graph(graph, bot_probabilities, positive_energies, out_degrees, in_degrees)
    print(type(energy_graph)) #> <class 'networkx.classes.digraph.DiGraph'>
    print(len(pl)) #> 7
    print(len(user_data)) #> 12
    # assert list(energy_graph.nodes) == [
    #     'user1', 'leader1', 'user2', 'user3', 'leader2', 'user4', 'user5', 'leader3',
    #     'colead1', 'colead2', 'colead4', 'colead3', 0, 1 # what's up with the extra 0 and 1 in here?
    # ]
    #
    # assert pl == ['user1', 'user4', 'colead4', 'user3', 'user5', 'colead1', 'user2'] # what does this list represent?
    #
    # assert user_data == {
    #     'user1': {'user_id': 'user1', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'leader1': {'user_id': 'leader1', 'out': 0, 'in': 100.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'user2': {'user_id': 'user2', 'out': 60.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'user3': {'user_id': 'user3', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'leader2': {'user_id': 'leader2', 'out': 0, 'in': 60.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'user4': {'user_id': 'user4', 'out': 20.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'user5': {'user_id': 'user5', 'out': 40.0, 'in': 0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'leader3': {'user_id': 'leader3', 'out': 0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'colead1': {'user_id': 'colead1', 'out': 30.0, 'in': 20.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'colead2': {'user_id': 'colead2', 'out': 20.0, 'in': 30.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'colead3': {'user_id': 'colead3', 'out': 10.0, 'in': 40.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0},
    #     'colead4': {'user_id': 'colead4', 'out': 40.0, 'in': 10.0, 'old_prob': 0.5, 'phi_0': 0.6931471805599453, 'phi_1': 0.6931471805599453, 'prob': 0, 'clustering': 0}
    # }
    #
    # todo: write pl users list to csv (see writeCSVFile in ioHELPER)
    # todo: write energy graph edges to CSV file (see writeCSVFile_H in ioHELPER)

    print("----------------------")
    print("COMPUTING BOT PROBABILITIES...")

    clustering = dict.fromkeys(list(user_data.keys()), 0)
    for user in pl:
        user_data[user]["clustering"] = 1
        clustering[user] = 1
    pprint(clustering)
    assert clustering == {
        'colead1': 1,
        'colead2': 0, 'colead3': 0,
        'colead4': 1,
        'leader1': 0, 'leader2': 0, 'leader3': 0,
        'user1': 1, 'user2': 1, 'user3': 1, 'user4': 1, 'user5': 1
    }

    exit()

    results=[]
    for i in range(0, nproc - 1):
        r = comm.recv(source=i)
        results.append(r)

    bot_probabilities = {}
    for user, probability in results:
        bot_probabilities[user] = probability

    # todo: write_bot_probabilities_to_csv(csv_filepath, bot_probabilities)
