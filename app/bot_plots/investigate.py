
import os
from collections import Counter
from pprint import pprint

#from pandas import to_numeric
from app.retweet_graphs_v2.graph_storage import GraphStorage

DATE = "2020-01-23"
BOT_MIN = 0.8

storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/1/{DATE}")

retweet_graph = storage.load_graph()
print("NODES:", retweet_graph.number_of_nodes())

df = storage.load_bot_probabilities()
df["bot_probability"] = df["bot_probability"].astype(float)
df.rename(columns={"screen_name": "user_id"}, inplace=True)

bots_df = df[df["bot_probability"] >= BOT_MIN]
bot_ids = bots_df["user_id"].tolist()
print("BOTS:", len(bots_df))

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
breakpoint()
