
import os
from collections import Counter
from pprint import pprint

#from pandas import to_numeric
from numpy import arange # Return evenly spaced values within a given interval
from umap import UMAP
from networkx import adjacency_matrix
from matplotlib import pyplot as plt
#import umap.plot

from app.retweet_graphs_v2.graph_storage import GraphStorage

DATE = "2020-01-23"
BOT_MIN = 0.8

#
# RETWEET GRAPH
#

retweet_graph_storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/1/{DATE}")

retweet_graph = retweet_graph_storage.load_graph()
print("NODES:", retweet_graph.number_of_nodes()) #> 335,379

df = retweet_graph_storage.load_bot_probabilities()
df["bot_probability"] = df["bot_probability"].astype(float)
df.rename(columns={"screen_name": "user_id"}, inplace=True)

bots_df = df[df["bot_probability"] >= BOT_MIN]
bot_ids = bots_df["user_id"].tolist()
print("BOTS:", len(bots_df)) #> 5034

source_ids = [] # users retweeted by the bots
for user_id in retweet_graph.nodes():
    if user_id in bot_ids:
        # A predecessor of n is a node m such that there exists a directed edge from m to n.
        # A successor of n is a node m such that there exists a directed edge from n to m.
        #print("  ", len(list(retweet_graph.predecessors(user_id))), len(list(retweet_graph.successors(user_id)))) #> 0, 29
        source_ids += retweet_graph.successors(user_id) #> <class 'dict_keyiterator'>
print("BOT RETWEET BENEFICIARIES:", len(source_ids))

source_counter = Counter(source_ids)
pprint(source_counter.most_common(10))

# users retweeted by at least X bots
SOURCE_MIN = 100 # considered a beneficiary if at least this many bots are retweeting you on a given day
#top_source_ids = list([user_id for user_id in source_counter.keys() if source_counter[user_id] >= SOURCE_MIN])
top_source_ids = [k for k, v in source_counter.items() if v >= SOURCE_MIN]
# TODO: why top X?
# TODO: should we ensure no bots are in the source list?

#
# FOLLOWER GRAPH
#

follower_graph_storage = GraphStorage(dirpath=f"bot_follower_graphs/bot_min/{BOT_MIN}")
follower_graph = follower_graph_storage.load_graph() # buckle up this might take a while...

bot_follower_subgraph = follower_graph.subgraph(bot_ids).copy()
bot_follower_matrix = adjacency_matrix(bot_follower_subgraph)
#print("FOLLOWER SUBGRAPH", type(bot_follower_subgraph)) #> <class 'networkx.classes.digraph.DiGraph'>
print("FOLLOWER MATRIX", type(bot_follower_matrix), bot_follower_matrix.shape) #> <class 'scipy.sparse.csr.csr_matrix'> (4872, 4872)

MIN_DIST = 1
N_NEIGHBORS = 25
reducer = UMAP(metric="cosine", min_dist=MIN_DIST, n_neighbors=N_NEIGHBORS)
#print("REDUCER:", type(reducer)) #> <class 'umap.umap_.UMAP'>

embedding = reducer.fit_transform(bot_follower_matrix) # also takes a while...
print("EMBEDDING:", type(embedding), embedding.shape) #> <class 'numpy.ndarray'> (4872, 2)

means = embedding.mean(axis=0, keepdims=True) #> array([[5.803594 , 2.9446957]], dtype=float32)
bot_coords = embedding - means

colors = arange(bot_follower_matrix.shape[0]) #> (4872,)

breakpoint()

plt.scatter(bot_coords[:,0], bot_coords[:,1], c=colors)
plt.grid()
plt.title("Bots")
plt.show()
