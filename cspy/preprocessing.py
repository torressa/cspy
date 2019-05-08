import sys


def check_graph(G):
    if 'Source' in G.nodes() and 'Sink' in G.nodes():
        return G
    else:
        sys.exit("Input graph must have 'Source' and 'Sink' nodes")


def prune_graph(G):
    return G


def preprocess(G):
    G = check_graph(G)
    G = prune_graph(G)
    return G
