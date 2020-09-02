
import os

from app.retweet_graphs_v2.graph_storage import GraphStorage

# for a given day, load daily retweet graph and bot probabilities:

storage = GraphStorage(dirpath="retweet_graphs_v2/k_days/1/2020-01-01")

rt_graph = storage.load_graph()
print(type(rt_graph))

bot_probabilities_df = storage.load_bot_probabilities()
print(bot_probabilities_df.head())

#breakpoint()
