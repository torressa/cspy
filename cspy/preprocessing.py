import logging
import networkx as nx


def check(G, max_res=None, min_res=None, direc_in=None):
    """Check whether inputs have the appropriate attributes and
    are of the appropriate types."""

    def _check_res():
        if isinstance(max_res, list) and isinstance(min_res, list):
            if len(max_res) == len(min_res) >= 2:
                if (all(isinstance(i, (float, int)) for i in max_res) and
                        all(isinstance(i, (float, int)) for i in min_res)):
                    pass
                else:
                    raise Exception("Elements of input lists must be numbers")
            else:
                raise Exception("Input lists have to be equal length >= 2")
        else:
            raise Exception("Inputs have to be lists with length >= 2")

    def _check_direction():
        if direc_in not in ['forward', 'backward', 'both']:
            raise Exception(
                "Input direction has to be 'forward', 'backward', or 'both'")

    def _check_graph_attr():
        """Checks whether input graph has n_res attribute"""
        if isinstance(G, nx.DiGraph):
            if 'n_res' not in G.graph:
                raise Exception("Input graph must have 'n_res' attribute.")
        else:
            raise Exception("Input must be a nx.Digraph()")

    def _check_edge_attr():
        """Checks whether edges in input graph have res_cost attribute"""
        if not all('res_cost' in edge[2] for edge in G.edges(data=True)):
            raise Exception(
                "Input graph must have edges with 'res_cost' attribute.")

    def _check_path():
        """Checks whether a 'Source' -> 'Sink' path exists.
        Also covers nodes missing and other standard networkx exceptions"""
        try:
            nx.has_path(G, 'Source', 'Sink')
        except nx.NetworkXException as e:
            raise Exception("An error occured: {}".format(e))

    errors = []
    # Select checks to perform based on the input provided
    if max_res and min_res and direc_in:
        check_funcs = [_check_res, _check_direction, _check_graph_attr,
                       _check_edge_attr, _check_path]
    elif max_res and min_res:
        check_funcs = [_check_res, _check_graph_attr,
                       _check_edge_attr, _check_path]
    else:
        check_funcs = [_check_path]
    # Check all functions in check_funcs
    for func in check_funcs:
        try:
            func()
        except Exception as e:
            errors.append(e)  # if check fails save error message
    if errors:
        # if any check has failed raise an exception with all the error
        # messages
        raise Exception('\n'.join('{}'.format(item) for item in errors))


def prune_graph(G, max_res, min_res):
    """Removes nodes that cannot be reached due to resource limits.

    Parameters
    ----------

    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

     max_res : list of floats
        :math:`[L, M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    min_res : list of floats
        :math:`[U, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    Raises
    ------

    Raises exceptions if incorrect input is given. If multiple exceptions are
    raised, and exception with a list of exceptions is raised.

    Returns
    -------
    Preprocessed graph G
    """

    def _check_resource(r):
        # check resource r's feasibility along a path

        def _get_weight(i, j, attr_dict):
            # returns number to use as weight for the algorithm
            return attr_dict['res_cost'][r]

        # Get paths from source to all other nodes
        length, path = nx.single_source_bellman_ford(
            G, 'Source', weight=_get_weight)
        try:
            # If any path violates the resource upper or lower bounds
            # then, add the problematic node to the dictionary
            nodes_to_remove.update({
                path[key][-2]: val for key, val in length.items()
                if val > max_res[r] or val < min_res[r]})
            if "Source" in nodes_to_remove or "Sink" in nodes_to_remove:
                raise Exception("Sink not reachable for resource {}".format(r))
            # path is a dict of the form:
            # {node_i: [Source, ..., node_k, node_i]}.
            # Hence, if node_i is found to violate a resource constraint, it is
            # because of node_k, therefore, we add path[key][-2] = node_k to
            # the dictionary of nodes to remove.
        except IndexError:  # No nodes violate resource limits
            pass

    nodes_to_remove = {}
    # Map function for each resource
    list(map(_check_resource, range(0, G.graph['n_res'])))
    if nodes_to_remove:  # if there are nodes to remove
        # Filter out source or sink
        nodes_to_remove = {
            key: val for key, val in nodes_to_remove.items()
            if key != 'Source' or key != 'Sink'}
        G.remove_nodes_from(nodes_to_remove)
        logging.info("[{0}] Removed {1} nodes".format(
            __name__, len(nodes_to_remove)))
    return G


def check_and_preprocess(preprocess, G, max_res=None, min_res=None,
                         direction=None):
    """
    Checks whether inputs and the graph are of the appropriate types and
    have the required properties.
    Removes nodes that cannot be reached due to resource limits.

    Parameters
    ----------
    ``preprocess`` : bool
        enables preprocessing routine.

    ``G`` : object instance ``nx.Digraph()``
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    ``max_res`` : list of floats, optional
        :math:`[L, M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    ``min_res`` : list of floats, optional
        :math:`[U, L_1, L_2, ..., L_{nres}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    ``direction`` : string, optional
        preferred search direction. Either 'both','forward', or, 'backward'.
        Default : 'both'.

    :return: If ``preprocess``, returns preprocessed graph ``G`` if no
        exceptions are raised, otherwise doesn't return anything.

    :raises: Raises exceptions if incorrect input is given. If multiple exceptions are
        raised, and exception with a list of exceptions is raised.
    """
    check(G, max_res, min_res, direction)
    if preprocess:
        G = prune_graph(G, max_res, min_res)
        check(G)
        return G
