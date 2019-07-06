from networkx import DiGraph, NetworkXException, has_path


__all__ = ["_check_res", "_check_direction",
           "_check_graph_attr", "_check_edge_attr", "_check_path"]


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


def _check_path(G, max_res, min_res, direction, algorithm):
    """Checks whether a 'Source' -> 'Sink' path exists.
    Also covers nodes missing and other standard networkx exceptions"""
    try:
        has_path(G, 'Source', 'Sink')
    except NetworkXException as e:
        raise Exception("An error occurred: {}".format(e))
