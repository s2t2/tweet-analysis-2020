
import os
from collections import Counter

#from pandas import to_numeric
from app.retweet_graphs_v2.graph_storage import GraphStorage

BOT_MIN = 0.8
DATE = "2020-01-23"

storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/1/{DATE}")

df = storage.load_bot_probabilities()
df["bot_probability"] = df["bot_probability"].astype(float)
df.rename(columns={"screen_name": "user_id"}, inplace=True)

bots_df = df[df["bot_probability"] >= BOT_MIN]
bot_ids = bots_df["user_id"].tolist()
print("BOTS:", len(bots_df))

retweet_graph = storage.load_graph()
print("NODES:", retweet_graph.number_of_nodes())

sources = []
for user_id in retweet_graph.nodes():
    if user_id in bot_ids:
        # all retweets from the bot to others

        # A predecessor of n is a node m such that there exists a directed edge from m to n.
        # A successor of n is a node m such that there exists a directed edge from n to m.
        print(len(list(retweet_graph.predecessors(user_id))), len(list(retweet_graph.successors(user_id)))) #> 0, 29
        # the way I constructed the graphs I need to use successors here

        #sources += retweet_graph.predecessors(user_id) #> <class 'dict_keyiterator'>
        sources += retweet_graph.successors(user_id) #> <class 'dict_keyiterator'>


breakpoint()

#retweeted_user_ids = [retweet_graph.predecessors(user_id) for user_id in retweet_graph.nodes() if user_id in bot_ids]

source_counter = Counter(sources)

dmin = 100
sources = list([v for v in source_counter.keys() if source_counter[v]>=dmin])

print(source_counter.most_common(10))

print(f"{len(bot_ids)} BOTS HAVE RETWEETED {len(sources)} SOURCES")
