import os
import networkx as nx
import pandas

from app.storage_service import BigQueryService

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "network.gpickle")

CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "example_network.csv")
# columns: screen_name, friend_1, friend_2, friend_3, friend_4, etc...

def compile_nodes_and_edges(screen_names, csv_filepath=CSV_FILEPATH):
    """
    Given the following network:

        A doesn't follow anyone
        B follows A
        C follows B and A
        D and E follow eachother

    Returns nodes and edges...

        Nodes: {'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1}

        Edges: [('A', 'B'), ('B', 'C'), ('A', 'C'), ('E', 'D'), ('D', 'E')]

    Can read each edge tuple like: "0 is followed by 1"
    """
    nodes = {}
    for screen_name in screen_names:
        nodes[screen_name] = 1

    edges = []
    with open(csv_filepath) as csv_file:
        for index, line in enumerate(csv_file):
            #print("-------------")
            user_friends = line.strip("\n").split(",")
            user_name = user_friends[0] # follower
            friend_names = user_friends[1:] # friends
            #print("USER:", user_name, "FRIENDS:", friend_names)

            for friend_name in friend_names:
                if friend_name in nodes.keys():
                    edges.append((friend_name, user_name)) # 0 is followed by 1

    return nodes, edges

def generate_graph(edges):
    """
    Converts edges into a networkx digraph object.

    Param edges (list of tuples)
        ... like [('A', 'B'), ('B', 'C'), ('A', 'C'), ('E', 'D'), ('D', 'E')]
        ... where 'B' follows 'A', 'C' follows 'B', etc.

    Returns graph (networkx.classes.digraph.DiGraph)
    """
    graph = nx.DiGraph()
    for edge in edges:
        source = edge[0] # source, a.k.a friend, a.k.a followed
        recipient = edge[1] # recipient, a.k.a user, a.k.a follower
        graph.add_node(source)
        graph.add_node(recipient)
        graph.add_edge(source, recipient)
    return graph

if __name__ == "__main__":

    #df = pandas.read_csv(CSV_FILEPATH, header=None)
    #screen_names = df[0].tolist()
    #nodes, edges = compile_nodes_and_edges(screen_names)
    #print("NODE COUNT:", len(nodes))
    #print("EDGE COUNT:", len(edges))

    graph = generate_graph(edges)
    print(type(graph)) #> <class 'networkx.classes.digraph.DiGraph'>

    service = BigQueryService.cautiously_initialized()
    user_friends = service.fetch_user_friends(limit=20)

    breakpoint()
    graph = nx.DiGraph()
    for edge in edges:
        source = edge[0] # source, a.k.a friend, a.k.a followed
        recipient = edge[1] # recipient, a.k.a user, a.k.a follower
        graph.add_node(source)
        graph.add_node(recipient)
        graph.add_edge(source, recipient)

    print("WRITING NETWORK GRAPH TO:", GPICKLE_FILEPATH)
    nx.write_gpickle(graph, GPICKLE_FILEPATH)
