
# TODO: move this into the clustering.py file

from networkx import adjacency_matrix, Graph
from sklearn.cluster import SpectralClustering

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
