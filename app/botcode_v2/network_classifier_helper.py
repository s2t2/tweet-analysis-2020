
#
# A NEAR REPLICA OF BOTCODE VERSION 2 (SEE THE "START" DIR)
#

import math
from collections import defaultdict
from operator import itemgetter
import time

import numpy as np
import networkx as nx

##########################################################################
####################### BUILD RETWEET NX-(SUB)GRAPH FROM DICTIONNARY #####
##########################################################################
'''
Takes as input a csv file of retweet relationships and builds
a NetworkX object, in order to apply prebuilt mincut algorithms
'''


def buildRTGraph(graph, subNodes, lowerBound=0):
    '''
    INPUTS:
    ## graph (csv file)
        a csv file with ID of user retweeting, user retweeted, and number of retweets. (see README for more details)
    ## subNodes (list of ints)
        a list of users IDs if you want to only consider a subgraph of the RT graph
    ## lowerBound (int)
        an int to only consider retweet relationship if retweet count from User1 to User2 is above bound (sparsify graph)
    '''
    G = nx.DiGraph()
    count = 0
    firstInter = list(np.unique(np.intersect1d(subNodes, list(graph.keys()))))
    for node in firstInter:
        count += 1
        print("at user n" + str(count) + " on " + str(len(graph)))
        unique2, counts = np.unique(graph[node], return_counts=True)
        res = dict(zip(unique2, counts))
        inter = np.unique(np.intersect1d(unique2, subNodes))
        for i in inter:
            w = res[i]
            if(i != node and w >= lowerBound):
                G.add_node(node)
                G.add_node(i)
                G.add_edge(node, i, weight=w)

    return G


############################################################################
####################### BUILD/CUT ENERGY GRAPH #############################
############################################################################
'''
Takes as input the RT graph and builds the energy graph.
Then cuts the energy graph to classify
'''


def computeH(G, piBot, edgelist_data, graph_out, graph_in):
    H = nx.DiGraph()
    '''
    INPUTS:
    ## G (ntwkX graph)
        the Retweet Graph from buildRTGraph
    ## piBot (dict of floats)
        a dictionnary with prior on bot probabilities. Keys are users_ids, values are prior bot scores.
    ## edgelist_data (list of  tuples)
        information about edges to build energy graph.
        This list comes in part from the getLinkDataRestrained method
    ## graph_out (dict of ints)
        a graph that stores out degrees of accounts in retweet graph
    ## graph_in (dict of ints)
        a graph that stores in degrees of accounts in retweet graph

    '''
    user_data = {i: {
        'user_id': i,
        'out': graph_out[i],
        'in': graph_in[i],
        'old_prob': piBot[i],
        'phi_0': max(0, -np.log(float(10**(-20) + (1 - piBot[i])))),
        'phi_1': max(0, -np.log(float(10**(-20) + piBot[i]))),
        'prob': 0,
        'clustering': 0
    } for i in G.nodes()}

    set_1 = [(el[0], el[1]) for el in edgelist_data]
    set_2 = [(el[1], el[0]) for el in edgelist_data]
    set_3 = [(el, 0) for el in user_data]
    set_4 = [(1, el) for el in user_data]

    H.add_edges_from(set_1 + set_2 + set_3 + set_4, capacity=0)

    for i in edgelist_data:

        val_00 = i[2][0]
        val_01 = i[2][1]
        val_10 = i[2][2]
        val_11 = i[2][3]

     # edges between nodes
        H[i[0]][i[1]]['capacity'] += 0.5 * (val_01 + val_10 - val_00 - val_11)
        H[i[1]][i[0]]['capacity'] += 0.5 * (val_01 + val_10 - val_00 - val_11)

     # edges to sink (bot energy)
        H[i[0]][0]['capacity'] += 0.5 * val_11 + 0.25 * (val_10 - val_01)
        H[i[1]][0]['capacity'] += 0.5 * val_11 + 0.25 * (val_01 - val_10)

     # edges from source (human energy)
        H[1][i[0]]['capacity'] += 0.5 * val_00 + 0.25 * (val_01 - val_10)
        H[1][i[1]]['capacity'] += 0.5 * val_00 + 0.25 * (val_10 - val_01)

        if(H[1][i[0]]['capacity'] < 0):
            print("Neg capacity")
            break
        if(H[i[1]][0]['capacity'] < 0):
            print("Neg capacity")
            break
        if(H[1][i[1]]['capacity'] < 0):
            print("Neg capacity")
            break
        if(H[i[0]][0]['capacity'] < 0):
            print("Neg capacity")
            break

    for i in user_data.keys():
        H[1][i]['capacity'] += user_data[i]['phi_0']
        if(H[1][i]['capacity'] < 0):
            print("Neg capacity")
            break

        H[i][0]['capacity'] += user_data[i]['phi_1']
        if(H[i][0]['capacity'] < 0):
            print("Neg capacity")
            break

    cut_value, mc = nx.minimum_cut(H, 1, 0)
    # mc = [nodes dont cut source edge (bots), nodes dont cut sink edge
    # (humans)]
    Bots = list(mc[0])
    if 0 in Bots:  # wrong cut set because nodes have sink edge (humans)
        print("Double check")
        Bots = list(mc[1])
    Bots.remove(1)

    return H, Bots, user_data

def compute_bot_probabilities(rt_graph, energy_graph, bot_names):
    #print("Calculate bot probability for each labeled node in retweet graph")
    #start_time = time.time()
    PiBotFinal = {}

    for counter, node in enumerate(rt_graph.nodes()):
        #if counter % 1000 == 0: print("NODE:", counter)

        neighbors = list(np.unique([i for i in nx.all_neighbors(energy_graph, node) if i not in [0, 1]]))
        ebots = list(np.unique(np.intersect1d(neighbors, bot_names)))
        ehumans = list(set(neighbors) - set(ebots))

        psi_l = sum([energy_graph[node][j]['capacity'] for j in ehumans]) - \
            sum([energy_graph[node][i]['capacity'] for i in ebots])

        # probability to be in 1 = notPL
        psi_l_bis = psi_l + energy_graph[node][0]['capacity'] - energy_graph[1][node]['capacity']

        if (psi_l_bis) > 12:
            PiBotFinal[node] = 0
        else:
            # Probability in the target (0) class
            PiBotFinal[node] = 1.0 / (1 + np.exp(psi_l_bis))

    #print("--- %s seconds ---" % (time.time() - start_time))
    return PiBotFinal

###############################################################################
####################### COMPUTE EDGES INFORMATION #############################
###############################################################################
'''
Takes as input the RT graph and retrieves information on edges
to further build H.
'''


def getLinkDataRestrained(G, weight_attr="weight"):
    '''
    INPUTS:
    ## G (ntwkX graph)
        the Retweet Graph from buildRTGraph
    '''
    edges = G.edges(data=True)
    e_dic = dict(((x, y), z[weight_attr]) for x, y, z in edges)
    link_data = []
    for e in e_dic:
        i = e[0]
        j = e[1]
        rl = False
        wrl = 0
        if((j, i) in e_dic.keys()):
            rl = True
            wrl = e_dic[(j, i)]
        link_data.append([i, j, True, rl, e_dic[e], wrl])
    return link_data


##########################################################################
####################### POTENTIAL FUNCTION ###############################
##########################################################################
'''
Compute joint energy potential between two users
'''

# INPUTS:
# u1 (int) 		ID of user u1
# u2 (int) 		ID of user u2
# wlr (int) 		number of retweets from u1 to u2
# out_graph (dict of ints) 		a graph that stores out degrees of accounts in retweet graph
# in_graph (dict of ints) 		a graph that stores in degrees of accounts in retweet graph
# alpha (list of floats)
# a list containing hyperparams (mu, alpha_out, alpha_in)
# lambda00 = ratio of psi_00 to psi_01
# lambda11 = ratio of psi_11 to psi_01
## epsilon (int)
# exponent such that lambda01=lambda11+lambda00-1+epsilon


def psi(u1, u2, wlr, in_graph, out_graph, alpha, lambda00, lambda11, epsilon):
    dout_u1 = out_graph[u1]  # outdegree of u1 (number of retweets it did)
    din_u2 = in_graph[u2]  # indegree of u2 (number of retweets it received)

    if dout_u1 == 0 or din_u2 == 0:
        print("Relationship problem: " + str(u1) + " --> " + str(u2))

    temp = alpha[1] / float(dout_u1) - 1 + alpha[2] / float(din_u2) - 1

    if temp < 10:
        psi_01 = wlr * alpha[0] / (1 + np.exp(temp))
    else:
        psi_01 = 0
    lambda01 = 1
    lambda10 = lambda00 + lambda11 - 1 + epsilon

    psi_00 = lambda00 * psi_01
    psi_01 = lambda01 * psi_01
    psi_10 = lambda10 * psi_01
    psi_11 = lambda11 * psi_01

    return [psi_00, psi_01, psi_10, psi_11]
