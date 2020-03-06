from networkx import (DiGraph, NetworkXException, NetworkXUnbounded, has_path,
                      negative_edge_cycle)
from numpy import ndarray

__all__ = [
    "_check_res", "_check_direction", "_check_graph_attr", "_check_edge_attr",
    "_check_path", "_check_REFs"
]


def _check_res(G, max_res, min_res, direction, algorithm):
    if isinstance(max_res, list) and isinstance(min_res, list):
        if len(max_res) == len(min_res):
            if (algorithm and 'bidirectional' in algorithm and
                    len(max_res) < 2):
                raise TypeError("Resources must be of length >= 2")
            if (all(isinstance(i, (float, int)) for i in max_res) and
                    all(isinstance(i, (float, int)) for i in min_res)):
                pass
            else:
                raise TypeError("Elements of input lists must be numbers")
        else:
            raise TypeError("Input lists have to be equal length")
    else:
        raise TypeError("Inputs have to be lists with length >= 2")


def _check_direction(G, max_res, min_res, direction, algorithm):
    if direction not in ['forward', 'backward', 'both']:
        raise TypeError(
            "Input direction has to be 'forward', 'backward', or 'both'")


def _check_graph_attr(G, max_res, min_res, direction, algorithm):
    """Checks whether input graph has n_res attribute"""
    if isinstance(G, DiGraph):
        if 'n_res' not in G.graph:
            raise TypeError("Input graph must have 'n_res' attribute.")
    else:
        raise TypeError("Input must be a nx.Digraph()")


def _check_edge_attr(G, max_res, min_res, direction, algorithm):
    """Checks whether edges in input graph have res_cost attribute"""
    if not all('res_cost' in edge[2] for edge in G.edges(data=True)):
        raise TypeError(
            "Input graph must have edges with 'res_cost' attribute.")
    if not all(
            len(edge[2]['res_cost']) == G.graph['n_res']
            for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to 'n_res'")
    if not all(
            len(edge[2]['res_cost']) == len(max_res) == len(min_res)
            for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to" +
            "'min_res' == 'max_res")
    if not all(
            isinstance(edge[2]['res_cost'], ndarray)
            for edge in G.edges(data=True)):
        raise TypeError("The edge 'res_cost' attribute must be a numpy.array")


def _check_path(G, max_res, min_res, direction, algorithm):
    """Checks whether a 'Source' -> 'Sink' path exists and if there are
    negative edge cycles in the graph.
    Also covers nodes missing and other standard networkx exceptions."""
    try:
        if not has_path(G, 'Source', 'Sink'):
            raise NetworkXException("Disconnected Graph")
        if negative_edge_cycle(G):
            raise NetworkXException("A negative cost cycle was found.")
    except NetworkXException as e:
        raise Exception("An error occurred: {}".format(e))


def _check_REFs(REF_forward, REF_backward):
    if (REF_forward and not callable(REF_forward)) or (
            REF_backward and
            not callable(REF_backward)) or (REF_forward and REF_backward and
                                            not callable(REF_forward) and
                                            not callable(REF_backward)):
        raise TypeError("REF functions must be callable")
