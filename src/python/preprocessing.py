from copy import deepcopy
from logging import getLogger
from networkx import single_source_bellman_ford
from cspy.checking import check

log = getLogger(__name__)


def prune_graph(G, max_res, min_res):
    """
    Graph pruning to remove unreachable nodes.

    Note
    -----
    path_s and path_t contains all partial paths e.g.
        {node_i: [Source, ..., node_k, node_i]}.
    or  {node_i: [Sink, ..., node_k, node_i]}
    Hence, if node_i is found to violate a resource bound, it is
    because of node_k, therefore, we add path[key][-2] = node_k to
    the dictionary of nodes to remove.
    """

    def _check_resource(r):
        # check resource r's feasibility along a path

        def __get_weight(i, j, attr_dict):
            # returns number to use as weight for the algorithm
            return attr_dict['res_cost'][r]

        # Get paths from source to all other nodes
        length_s, path_s = single_source_bellman_ford(G,
                                                      'Source',
                                                      weight=__get_weight)
        length_t, path_t = single_source_bellman_ford(G.reverse(copy=True),
                                                      'Sink',
                                                      weight=__get_weight)
        try:
            # Collect nodes in paths that violate the resource bounds
            # see note above
            nodes_source.update({
                path_s[key][-2]: (val, r)
                for key, val in length_s.items()
                if val > max_res[r] or val < min_res[r]
            })
            nodes_sink.update({
                path_t[key][-2]: (val, r)
                for key, val in length_t.items()
                if val > max_res[r] or val < min_res[r]
            })
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
            if "Sink" in nodes_source:
                unreachable_res = nodes_source["Sink"][1]
            elif "Sink" in nodes_sink:
                unreachable_res = nodes_sink["Sink"][1]
            elif "Source" in nodes_sink:
                unreachable_res = nodes_sink["Source"][1]
            elif "Source" in nodes_source:
                unreachable_res = nodes_source["Source"][1]
            raise Exception(
                "Sink not reachable for resource {}".format(unreachable_res))
        G.remove_nodes_from(nodes_to_remove)
        log.info("Removed {}/{} nodes".format(len(nodes_to_remove), n_nodes))
    return G


def preprocess_graph(
    G,
    max_res,
    min_res,
    preprocess,
    REF=None,
):
    """
    Applies preprocessing that removes nodes that cannot be reached due to
    resource limits.

    Parameters
    ----------
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

    preprocess : bool
        enables preprocessing routine.

    :return: If ``preprocess`` is True, returns the preprocessed graph if no
        exceptions are raised.

    """
    if REF:
        # Cannot apply pruning with custom REFs
        return deepcopy(G.copy())
    if preprocess:
        G = prune_graph(G, max_res, min_res)
        check(G)
    return deepcopy(G.copy())
