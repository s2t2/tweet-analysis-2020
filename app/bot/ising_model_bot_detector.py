
import os
import datetime
import time

import numpy as np
from pandas import DataFrame

#import matplotlib.pyplot as plt
#from sklearn import metrics
#from scipy.sparse import csc_matrix

from conftest import compile_mock_rt_graph, mock_rt_graph_edge_list
from app.workers import fmt_n, fmt_pct
from app.graph_analyzer import GraphAnalyzer
from app.bot.network_classifier_helper import getLinkDataRestrained as get_link_data_restrained
from app.bot.network_classifier_helper import psi as link_energy
from app.bot.network_classifier_helper import computeH as compile_energy_graph
from app.bot.network_classifier_helper import compute_bot_probabilities



if __name__ == "__main__":

    #
    # LOAD GRAPH (GIVEN JOB ID)
    #
    print("----------------")
    rt_graph = compile_mock_rt_graph(mock_rt_graph_edge_list) # mock_rt_graph()

    manager = GraphAnalyzer()
    #manager.report()
    #rt_graph = manager.graph

    print("RT GRAPH:", type(rt_graph))

    in_degrees = rt_graph.in_degree(weight="rt_count")
    out_degrees = rt_graph.out_degree(weight="rt_count")
    in_degrees_list = [x[1] for x in in_degrees]
    out_degrees_list = [x[1] for x in out_degrees]
    print("RTS IN MAX:", fmt_n(max(in_degrees_list))) #> 76,617
    print("RTS OUT MAX:", fmt_n(max(out_degrees_list))) #> 5,608

    print("----------------")
    print("ISING PARAMS...")

    mu = 1
    percentile = 0.999
    alpha_in = np.quantile(in_degrees_list, percentile)
    alpha_out = np.quantile(out_degrees_list, percentile)
    print("ALPHA IN:", fmt_n(alpha_in)) #> 2,252
    print("ALPHA OUT:", fmt_n(alpha_out)) #> 1,339
    alpha = [mu, alpha_out, alpha_in]

    epsilon = 10**(-3) #> 0.001
    #lambda01 = 1
    lambda00 = 0.61 # using this as a link energy param
    lambda11 = 0.83 # using this as a link energy param
    #lambda10 = lambda00 + lambda11 - lambda01 + epsilon

    #
    # CREATE ENERGY GRAPH
    #

    print("----------------")
    print("ENERGY GRAPHER...")

    links = get_link_data_restrained(rt_graph, weight_attr="rt_count") # this step is unnecessary?
    print("LINKS:", len(links))

    energies = [(
        link[0],
        link[1],
        link_energy(link[0], link[1], link[4], in_degrees, out_degrees, alpha, lambda00, lambda11, epsilon) # just loop through edges and pass the edges and "rt_count" data here?
    ) for link in links]
    print("ENERGIES:", fmt_n(len(energies)))

    #positive_energies = [e for e in energies if sum(e[2]) > 0]
    #print("POSITIVE ENERGIES:", fmt_n(len(positive_energies)))

    prior_probabilities = dict.fromkeys(list(rt_graph.nodes), 0.5) # set all screen names to 0.5
    energy_graph, bot_names, user_data = compile_energy_graph(rt_graph, prior_probabilities, energies, out_degrees, in_degrees)
    #human_names = list(set(rt_graph.nodes()) - set(bot_names))
    print("ENERGY GRAPH:", type(energy_graph))
    print("NODES:", energy_graph.number_of_nodes())
    print("BOTS:", fmt_n(len(bot_names)), "(", fmt_pct(len(bot_names) / energy_graph.number_of_nodes()), ")")

    #
    # BOT CLASSIFICATION
    #

    bot_probabilities = compute_bot_probabilities(rt_graph, energy_graph, bot_names)
    print("CLASSIFICATION COMPLETE!")

    #
    # WRITE TO FILE
    #

    df = DataFrame(list(bot_probabilities.items()), columns=["screen_name", "bot_probability"])
    print(df.head())
    csv_filepath = os.path.join(manager.local_dirpath, "bot_probabilities_202001010101.csv")
    df.to_csv(csv_filepath)
    print("WRITING TO FILE...")
    print(csv_filepath)

























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
