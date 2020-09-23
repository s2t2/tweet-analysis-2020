import json
import random
import csv
import numpy as np
from scipy import sparse

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
# code for helper file


def G_from_follower_graph(node_filename, follower_graph_filename, threshold_low, threshold_high):
    G = nx.DiGraph()
    print("Building network for Assess.\nStubborn intervals = (0,%.3f),(%.3f,1)" % (threshold_low, threshold_high))
    # first get the nodes and their info and add it to the graph object G
    data_nodes = pd.read_csv(node_filename)
    data_nodes.Stubborn = 1*np.logical_or(data_nodes.InitialOpinion <= threshold_low, data_nodes.InitialOpinion >= threshold_high)
    for row in data_nodes.iterrows():
        G.add_node(row[1]['id'],
            Name=row[1]['id'],
            InitialOpinion=row[1]['InitialOpinion'],
            Stubborn=row[1]['Stubborn'],
            Rate=row[1]['Rate'],
            FinalOpinion=row[1]['InitialOpinion'],
            Bot=row[1]['Bot']
        )

    # second, add the edges to the graph if both nodes are in the node set
    Edges = []
    ne = 0  # edge counter
    with open(follower_graph_filename) as fp:
        for cnt, line in enumerate(fp):
            line = line.strip('\n')
            users = line.split(",")
            follower = users[0]
            if follower in G.nodes():
                # followings is a list of the people the follower follows
                followings = users[1:]
                for following in followings:
                    if following in G.nodes():
                        ne += 1
                        rate = G.nodes[following]['Rate']
                        # edge points from the following to the follower - edge shows flow of tweets
                        G.add_edge(following, follower, Rate=rate)
    return G

def risk_index(Gbot0):
    Gnobot = Gbot0.subgraph([x for x in Gbot0.nodes if Gbot0.nodes[x]["Bot"] == 0])
    print("Solving for opinions with bots")
    (X, Gbot) = final_opinions(Gbot0)
    print("Solving for opinions without bots")
    (X, Gnobot) = final_opinions(Gnobot)
    OpinionsBot = []
    OpinionsNoBot = []
    print("Saving opinions to arrays")
    for node in Gbot.nodes():
        if Gbot.nodes[node]["Bot"] == 0:
            opinion_nobot = Gnobot.nodes[node]['FinalOpinion']
            opinion_bot = Gbot.nodes[node]['FinalOpinion']
        else:
            opinion_nobot = Gbot.nodes[node]['FinalOpinion']
            opinion_bot = Gbot.nodes[node]['FinalOpinion']
        OpinionsBot.append(opinion_bot)
        OpinionsNoBot.append(opinion_nobot)
    OpinionsBot = np.asarray(OpinionsBot)
    OpinionsNoBot = np.asarray(OpinionsNoBot)
    ri = np.mean(OpinionsBot-OpinionsNoBot)
    return (ri, OpinionsNoBot, OpinionsBot, Gnobot, Gbot)

# find all nodes reachable by a stubborn user and return corresponding subgraph


def reachable_from_stubborn(G):
    ne = G.number_of_edges()
    nv = G.number_of_nodes()
    V = {}  # keep track of all reachable nodes
    c = 0  # count how many nodes we iterate through
    cprint = 1e3  # how often to print status
    c_reach = 0  # count how many times we do reach calculation
    Stub = [v for v in G.nodes if G.nodes[v]['Stubborn'] == 1]
    nstub = len(Stub)
    print("Checking reachable nodes from %s stubborn nodes" % nstub)
    for node in Stub:
        # print(node)

        if not(node in V):
            if (G.nodes[node]["Stubborn"] == 1) or (G.nodes[node]["Bot"] == 1):
                reach = nx.dfs_postorder_nodes(G, source=node, depth_limit=ne)
                V.update({i: 1 for i in [node]+list(reach)})
                # print("\t%s"%V)
                c_reach += 1
        c += 1
        if c % cprint == 0:
            print("Node %s of %s, did reach check for %s nodes" %
                  (c, nstub, c_reach))

    #V = list(set(V))
    print("Did reach check for only %s nodes out of %s" % (c_reach, nv))
    Gbot = G.subgraph(V)
    return (Gbot, V.keys())
