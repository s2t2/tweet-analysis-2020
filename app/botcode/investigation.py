


import os
from pprint import pprint

import numpy as np
from networkx import DiGraph

from app.botcode.network_classifier_helper import parse_bidirectional_links, compute_link_energy, compile_energy_graph
from app.workers import fmt_n

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

def classify_bot_probabilities(rt_graph, weight_attr="rt_count"):
    """
    Given a retweet graph, computes bot probabilities, in a single function!

    Params:

        rt_graph (networkx.DiGraph) representing a retweet graph, with weights stored in the weight_attr param

        weight_attr (str) the attribute in the edge data where the weights are.
            in the rt graph, this represents number of times user a has retweeted user b
    """

    in_degrees = dict(rt_graph.in_degree(weight=weight_attr)) # users receiving retweets
    out_degrees = dict(rt_graph.out_degree(weight=weight_attr)) # users doing the retweeting
    print("IN-DEGREES:", fmt_n(len(in_degrees)))
    print("OUT-DEGREES:", fmt_n(len(out_degrees)))

    links = parse_bidirectional_links(rt_graph)
    energies = [(link[0], link[1], compute_link_energy(link[0], link[1], link[4], in_degrees, out_degrees)) for link in links]
    print("ENERGIES:", fmt_n(len(energies)))
    positive_energies = [e for e in energies if sum(e[2]) > 0]
    print("POSITIVE ENERGIES:", fmt_n(len(positive_energies)))

    prior_probabilities = dict.fromkeys(list(rt_graph.nodes), 0.5)
    energy_graph, pl, user_data = compile_energy_graph(rt_graph, prior_probabilities, positive_energies, out_degrees, in_degrees)
    print("ENERGIES GRAPHED...") # this is the step that takes the longest

    bot_probabilities = dict.fromkeys(list(user_data.keys()), 0) # start with defaults of 0 for each user
    for user in pl:
        user_data[user]["clustering"] = 1
        bot_probabilities[user] = 1

    return bot_probabilities, user_data

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
    prior_probabilities = dict.fromkeys(nodes, 0.5) # no priors, set all at 0.5!
    #print(prior_probabilities) #> {'user1': 0.5, 'user2': 0.5, 'user3': 0.5}

    print("----------------------")
    print("CONSTRUCTING RETWEET ENERGY GRAPH...")
    energy_graph, pl, user_data = compile_energy_graph(graph, prior_probabilities, positive_energies, out_degrees, in_degrees)
    print(type(energy_graph), len(pl), len(user_data)) #> <class 'networkx.classes.digraph.DiGraph'> 7 12
    print("PL:", pl)
    #pprint(user_data)
    # todo: write pl users list to csv (see writeCSVFile in ioHELPER)
    # todo: write energy graph edges to CSV file (see writeCSVFile_H in ioHELPER)


    print("----------------------")
    print("COMPUTING BOT PROBABILITIES...")

    bot_probabilities = dict.fromkeys(list(user_data.keys()), 0) # start with defaults of 0 for each user
    for user in pl:
        user_data[user]["clustering"] = 1
        bot_probabilities[user] = 1
    pprint(bot_probabilities)
    # assert bot_probabilities == {
    #     'colead1': 1, 'colead2': 0, 'colead3': 0, 'colead4': 1,
    #     'leader1': 0, 'leader2': 0, 'leader3': 0,
    #     'user1': 1, 'user2': 1, 'user3': 1, 'user4': 1, 'user5': 1
    # }

    # todo: write_bot_probabilities_to_csv(csv_filepath, bot_probabilities)
