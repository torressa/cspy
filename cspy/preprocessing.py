import sys


def check_graph(G):
    nodes = G.nodes()
    if 'Source' in nodes and 'Sink' in nodes:
        return G
    else:
        sys.exit("Input graph must have 'Source' and 'Sink' nodes")


def prune_graph(G):
    return G


def preprocess(G):
    G = check_graph(G)
    G = prune_graph(G)
    return G
