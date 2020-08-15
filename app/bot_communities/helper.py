
from networkx import adjacency_matrix, jaccard_coefficient, Graph, write_gpickle
import numpy as np
from sklearn.cluster import SpectralClustering

def generate_bot_similarity_graph(V, Gretweet):
    """
    Copied unchanged from the "start/bot_communities" notebook, then auto-converted to PEP8 style.

    Params:
        V (list) a unique list of bot ids, which should all be included as nodes in the bot retweet graph.
            The retweet graph will also contain retweeted users. So that's why we need a separate list.
            The bot ids will be used as nodes in the similarity graph.

        Gretweet (networkx.DiGraph) a retweet graph generated from the bot list

    Returns a similarity graph (networkx.Graph), where the similarity is based on the Jaccard index.
        For each pair of bots we calculate the Jaccard index based on the sets of people they retweet.
        If two bots retweet exactly the same users, their Jaccard index is one.
        If they don't retweet anyone in common, their Jaccard index is zero.
    """

    ebunch = []
    for counter, u in enumerate(V):
        for v in V[counter + 1:]:
            if (Gretweet.has_node(v)) and (Gretweet.has_node(u)):
                ebunch.append((u, v))

    preds = jaccard_coefficient(Gretweet.to_undirected(), ebunch)
    print(len(ebunch), " node pairs to check Jaccard index")

    print("Create similarity graph between bots using Jaccard index based on retweets")
    counter = 0
    Gsim = Graph()
    ne = 0
    for u, v, s in preds:
        counter += 1
        if s > 0:
            Gsim.add_edge(u, v, weight=s)
            ne += 1
        if counter % 1e6 == 0:
            print(counter, ne, " positive weights")

    nv = Gsim.number_of_nodes()
    ne = Gsim.number_of_edges()
    print("Gsim has %s nodes, %s edges" % (nv, ne))

    return Gsim

def spectral_clustering(G, k=2):
    """
    Copied unchanged from the same function in the "start/bot_communities" directory.

    Assigns each node in the graph G to one of K communities.
    """

    A = adjacency_matrix(G.to_undirected())
    clustering = SpectralClustering(n_clusters=k, eigen_solver=None, affinity='precomputed', n_init=20)
    clusters = clustering.fit(A)
    Comm = [[] for i in range(k)]
    nv = 0 # index for the nodes cluster labels
    for node in G.nodes():
        node_comm = clustering.labels_[nv] # community membership of node converted to a python list index
        nv += 1
        X = Comm[node_comm] # community list of community c
        X.append(node) # add node to the appropriate community
        Comm[node_comm] = X  # add the community list to the big list of all communities
        #print("Node %s joined community %s which has %s nodes"%(node,node_comm,len(Comm[node_comm])))
        Comm.sort(reverse=True, key=len)
    return Comm
