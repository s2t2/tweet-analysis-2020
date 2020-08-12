
import os

from networkx import jaccard_coefficient, Graph, write_gpickle

from app.bot_communities.bot_retweet_grapher import BotRetweetGrapher

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


if __name__ == "__main__":

    grapher = BotRetweetGrapher()

    bot_retweet_graph = grapher.load_graph()

    bot_ids = list(grapher.bq_service.fetch_bot_ids(bot_min=grapher.bot_min))
    print("FETCHED", len(bot_ids), "BOT IDS")

    bot_similarity_graph = generate_bot_similarity_graph(bot_ids, bot_retweet_graph)

    print("SAVING SIMILARITY GRAPH...")
    local_similarity_graph_filepath = os.path.join(grapher.local_dirpath, "similarity_graph.gpickle")
    write_gpickle(bot_similarity_graph, local_similarity_graph_filepath)

    print("UPLOADING SIMILARITY GRAPH...")
    gcs_similarity_graph_filepath = os.path.join(grapher.gcs_dirpath, "similarity_graph.gpickle")
    grapher.upload_file(local_similarity_graph_filepath, gcs_similarity_graph_filepath)
