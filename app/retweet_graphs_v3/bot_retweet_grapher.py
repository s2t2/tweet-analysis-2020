
import os

from pandas import read_csv
from networkx import DiGraph

from app import APP_ENV
from app.file_storage import FileStorage
from app.bq_service import BigQueryService
from app.retweet_graphs_v3.retweet_grapher import RetweetGrapher

BOT_MIN = float(os.getenv("BOT_MIN", default="0.7"))

if __name__ == "__main__":

    grapher = RetweetGrapher()
    storage = grapher.storage

    graph = grapher.load_graph()
    bots_df = read_csv(os.path.join(storage.local_dirpath, "probabilities.csv"))
    bot_ids = bots_df[bots_df["bot_probability"] > BOT_MIN]["user_id"].tolist()

    #bot_subgraph = graph.subgraph(bot_ids) # keeps all bot nodes but only the edges between them, not edges outward
    #bot_subgraph = graph.edge_subgraph(bot_ids) # needs to know full edges

    bot_graph = DiGraph()
    for user_id, retweeted_user_id, attrs in graph.edges(data=True):
        if user_id in bot_ids:
            bot_graph.add_edge(user_id, retweeted_user_id, weight=attrs["weight"])

    breakpoint()
