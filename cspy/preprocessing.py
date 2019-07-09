import logging
import networkx as nx
from cspy.checks import *

log = logging.getLogger(__name__)


def check(G, max_res=None, min_res=None, direction=None, algorithm=None):
    """Check whether inputs have the appropriate attributes and
    are of the appropriate types."""

    errors = []
    # Select checks to perform based on the input provided
    if max_res and min_res and direction:
        check_funcs = [
            _check_res, _check_direction, _check_graph_attr, _check_edge_attr,
            _check_path
        ]
    elif max_res and min_res:
        check_funcs = [
            _check_res, _check_graph_attr, _check_edge_attr, _check_path
        ]
    else:
        check_funcs = [_check_path]
    # Check all functions in check_funcs
    for func in check_funcs:
        try:
            func(G, max_res, min_res, direction, algorithm)
        except Exception as e:
            errors.append(e)  # if check fails save error message
    if errors:
        # if any check has failed raise an exception with all the errors
        raise Exception('\n'.join('{}'.format(item) for item in errors))


def prune_graph(G, max_res, min_res):
    """Removes nodes that cannot be reached due to resource limits."""

    def _check_resource(r):
        # check resource r's feasibility along a path

        def __get_weight(i, j, attr_dict):
            # returns number to use as weight for the algorithm
            return attr_dict['res_cost'][r]

        # Get paths from source to all other nodes
        length_s, path_s = nx.single_source_bellman_ford(G,
                                                         'Source',
                                                         weight=__get_weight)
        length_t, path_t = nx.single_source_bellman_ford(G.reverse(copy=True),
                                                         'Sink',
                                                         weight=__get_weight)
        try:
            # Collect nodes in paths that violate the resource bounds
            nodes_source.update({
                path_s[key][-2]: val
                for key, val in length_s.items()
                if val > max_res[r] or val < min_res[r]
            })
            nodes_sink.update({
                path_t[key][-2]: val
                for key, val in length_t.items()
                if val > max_res[r] or val < min_res[r]
            })
            """
            path_s and path_t containts all partial paths e.g.
                {node_i: [Source, ..., node_k, node_i]}.
            or  {node_i: [Sink, ..., node_k, node_i]}
            Hence, if node_i is found to violate a resource bound, it is
            because of node_k, therefore, we add path[key][-2] = node_k to
            the dictionary of nodes to remove.
            """
        except IndexError:  # No nodes violate resource limits
            pass

    nodes_source = {}
    nodes_sink = {}
    n_nodes = len(G.nodes())
    # Map function for each resource
    list(map(_check_resource, range(0, G.graph['n_res'])))
    if nodes_source and nodes_sink:  # if there are nodes to remove
        # Filter out source or sink
        nodes_to_remove = [
            node for node in G.nodes() if node in nodes_source and nodes_sink
        ]
        if "Source" in nodes_to_remove or "Sink" in nodes_to_remove:
            raise Exception("Sink not reachable for resource {}".format(r))
        G.remove_nodes_from(nodes_to_remove)
        log.info("Removed {}/{} nodes".format(len(nodes_to_remove), n_nodes))
    return G


def check_and_preprocess(preprocess,
                         G,
                         max_res=None,
                         min_res=None,
                         direction=None,
                         algorithm=None):
    """
    Checks whether inputs and the graph are of the appropriate types and
    have the required properties.
    Removes nodes that cannot be reached due to resource limits.

    Parameters
    ----------
    preprocess : bool
        enables preprocessing routine.

    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    max_res : list of floats, optional
        :math:`[L, M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    min_res : list of floats, optional
        :math:`[U, L_1, L_2, ..., L_{nres}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    direction : string, optional
        preferred search direction. Either 'both','forward', or, 'backward'.
        Default : 'both'.

    :return: If ``preprocess``, returns preprocessed graph ``G`` if no
        exceptions are raised, otherwise doesn't return anything.

    :raises: Raises exceptions if incorrect input is given.
        If multiple exceptions are raised, and exception with a list of
        exceptions is raised.
    """
    check(G, max_res, min_res, direction, algorithm)
    if preprocess:
        G = prune_graph(G, max_res, min_res)
        check(G)
    return G
