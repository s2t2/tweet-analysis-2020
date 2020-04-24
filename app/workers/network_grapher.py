import os
import networkx as nx
import pandas

from app.storage_service import BigQueryService

GPICKLE_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "network.gpickle")

CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_network.csv")
# columns: screen_name, friend_1, friend_2, friend_3, friend_4, etc...

def compile_nodes_and_edges(screen_names, csv_filepath=CSV_FILEPATH, gpickle_filepath=GPICKLE_FILEPATH):
    """
    Returns nodes and edges.
        Example nodes: {"userA": 1, "userB": 1, "userC": 1}
        Example edges: [...]
    """
    nodes = {}
    for screen_name in screen_names:
        nodes[screen_name] = 1

    edges = []
    with open(csv_filepath) as csv_file:
        for index, line in enumerate(csv_file):
            names = line.strip("\n").split(",")
            user_name = names[0]
            friend_names = names[1:]

            for friend_name in friend_names:
                if friend_name in screen_names:
                    edges.append((friend_name, user_name))

    return nodes, edges

def write_networkx(nodes, edges):
    """
    Adapted from code in the "start" directory. Converts friends graph into a networkx object.
    """

    graph = nx.DiGraph()
    for edge in edges:
        source = edge[0]
        recipient = edge[1]
        graph.add_node(source)
        graph.add_node(recipient)
        graph.add_edge(source,recipient)

    #undirected = graph.to_undirected()
    ##print(sorted(undirected.nodes()))
    ##undirected.remove_node(target)
    #node_count = undirected.number_of_nodes()
    #edge_count = undirected.number_of_edges()

    nx.write_gpickle(graph, gpickle_filepath)
    print("WROTE NETWORKX GRAPH TO:", gpickle_filepath)
    return graph

    return edges, nodes

if __name__ == "__main__":

    #service = BigQueryService.cautiously_initialized()
    #user_friends = service.fetch_user_friends(limit=20)

    df = pandas.read_csv(CSV_FILEPATH, header=None)
    screen_names = df[0].tolist()

    nodes, edges = compile_nodes_and_edges(screen_names)
    print("NODE COUNT:", len(nodes))
    print("EDGE COUNT:", len(edges))
