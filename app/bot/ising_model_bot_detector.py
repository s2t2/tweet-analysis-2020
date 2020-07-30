
import os
import datetime
import time

import numpy as np
from networkx import all_neighbors
import pandas as pd

#import matplotlib.pyplot as plt
#from sklearn import metrics
#from scipy.sparse import csc_matrix

#from app.bot.network_classifier_helper import *
from app.graph_analyzer import GraphAnalyzer
from app.workers import fmt_n, fmt_d

#
# LOAD GRAPH (GIVEN JOB ID)
#

print("----------------")
manager = GraphAnalyzer()
rt_graph = manager.graph
manager.report()
#bot_probabilities_filepath = os.path.join(manager.local_dirpath, "bot_probabilities_202001010101.csv"

#
# IN/OUT DEGREES (GIVEN GRAPH)
#

in_degrees = rt_graph.in_degree(weight="rt_count")
out_degrees = rt_graph.out_degree(weight="rt_count")
in_degrees_list = [x[1] for x in in_degrees]
out_degrees_list = [x[1] for x in out_degrees]

print("----------------")
print("RTS IN MAX:", fmt_n(max(in_degrees_list))) #> 76,617
print("RTS OUT MAX:", fmt_n(max(out_degrees_list))) #> 5,608

# ISING PARAMS (GIVEN IN/OUT DEGREES)

print("----------------")
print("ISING PARAMS...")
mu = 1

epsilon = 10**(-3) #> 0.001
lambda01 = 1
lambda00 = 0.61
lambda11 = 0.83
lambda10 = lambda00 + lambda11 - lambda01 + epsilon

percentile = 0.999
alpha_in = np.quantile(in_degrees_list, percentile) #>
alpha_out = np.quantile(out_degrees_list, percentile) #>
print("ALPHA IN:", fmt_d(alpha_in))
print("ALPHA OUT:", fmt_d(alpha_out))

alpha = [mu, alpha_out, alpha_in]


#
# CREATE ENERGY GRAPH
#

breakpoint()

PiBot = {}
for v in rt_graph.nodes():
    PiBot[v] = 0.5
# link_data[i] = [u,v,is (u,v) in E, is (v,u) in E, number times u rewteets v]
link_data = getLinkDataRestrained(rt_graph)







breakpoint()

start_time = time.time()
print("Make edgelist_data")
# edgelist_data[i] = [u,v,(Psi00,Psi01,Psi10,Psi11)], these are the edge energies
# on edge (i,j) for the graph cut
edgelist_data = [(i[0], i[1], psi(i[0], i[1], i[4], in_degrees, out_degrees, alpha, lambda00, lambda11, epsilon)) for i in link_data]
print("\tEdgelist has %s edges" % len(edgelist_data))
print("--- %s seconds ---" % (time.time() - start_time))















#"""## Find Min-Cut of energy graph
#
#H = energy graph
#
#BotsIsing = list of nodes who are bots in min-cut
#
#HumansIsing = list of nodes who are humans in min-cut
#"""
#
#start_time = time.time()
#print("Cut graph")
#H, BotsIsing, user_data = computeH(rt_graph, PiBot, edgelist_data, out_degrees, in_degrees)
#Nodes = []
#for v in rt_graph.nodes():
#    Nodes.append(v)
#HumansIsing = list(set(Nodes) - set(BotsIsing))
#print('\tCompleted graph cut')
#print("%s bots in %s nodes" % (len(BotsIsing), rt_graph.number_of_nodes()))
#print("--- %s seconds ---" % (time.time() - start_time))
#
#"""## Calculate Bot Probability
#Find the probability each node is a bot using classification found from min-cut of energy graph.
#
#THIS TAKES A LONG TIME
#
#PiBotFinal = dictionary of bot probabilities.
#"""
#
#start_time = time.time()
#print("Calculate bot probability for each labeled node in retweet graph")
#PiBotFinal = {}
#
#for counter, node in enumerate(rt_graph.nodes()):
#    if counter % 1000 == 0:
#        print("Node %s" % counter)
#    if node in rt_graph.nodes():
#        neighbors = list(
#            np.unique([i for i in nx.all_neighbors(H, node) if i not in [0, 1]]))
#        ebots = list(np.unique(np.intersect1d(neighbors, BotsIsing)))
#        ehumans = list(set(neighbors) - set(ebots))
#        psi_l = sum([H[node][j]['capacity'] for j in ehumans]) - \
#            sum([H[node][i]['capacity'] for i in ebots])
#
#        # probability to be in 1 = notPL
#        psi_l_bis = psi_l + H[node][0]['capacity'] - H[1][node]['capacity']
#
#        if (psi_l_bis) > 12:
#            PiBotFinal[node] = 0
#        else:
#            # Probability in the target (0) class
#            PiBotFinal[node] = 1. / (1 + np.exp(psi_l_bis))
#
#
#print("--- %s seconds ---" % (time.time() - start_time))
#
#"""## Save probabilities to file
#Convert dictionary of bot probabilities to a dataframe and write to a csv file.
#"""
#
#dfPiBot = pd.DataFrame(list(PiBotFinal.items()), columns=['screen_name', 'bot_probability'])
#
#dfPiBot.to_csv(bot_probabilities_filepath)
#print("Wrote bot probabilities to %s" % bot_probabilities_filepath)

























exit()




"""## Histogram of Bot Probabilities
Plot a histogram of the bot probabilities so you can see what a good threshold is
"""

data = dfPiBot.bot_probability
num_bins = round(len(data) / 10)
counts, bin_edges = np.histogram(data, bins=num_bins, normed=True)
cdf = np.cumsum(counts)
plt.plot(bin_edges[1:], cdf / cdf[-1])
plt.grid()
plt.xlabel("Bot probability")
plt.ylabel("CDF")

nlow = len(dfPiBot[dfPiBot.bot_probability < 0.5])
nhigh = len(dfPiBot[dfPiBot.bot_probability > 0.5])
nmid = len(dfPiBot[dfPiBot.bot_probability == 0.5])
print(
    "%s users bot prob<0.5\n%s users bot prob>0.5\n%s users bot prob=0.5\n" %
     (nlow, nmid, nhigh))

plt.hist(dfPiBot.bot_probability[dfPiBot.bot_probability < 0.5])
plt.hist(dfPiBot.bot_probability[dfPiBot.bot_probability > 0.5])
plt.grid()
plt.xlabel("Bot probability")
plt.ylabel("Frequency")
plt.title("No 0.5 probability users")
