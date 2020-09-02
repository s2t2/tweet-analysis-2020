
import os

#from pandas import to_numeric
from app.retweet_graphs_v2.graph_storage import GraphStorage

BOT_MIN = 0.8
DATE = "2020-01-23"

storage = GraphStorage(dirpath=f"retweet_graphs_v2/k_days/1/{DATE}")

df = storage.load_bot_probabilities()
df["bot_probability"] = df["bot_probability"].astype(float)
#df["bot_probability"] = to_numeric(df["bot_probability"], errors="coerce")

bot_ids = df[df["bot_probability"] >= BOT_MIN]
print("BOTS:", len(bot_ids))









exit()





graph = storage.load_graph()
