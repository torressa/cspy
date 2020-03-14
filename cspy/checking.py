from networkx import (DiGraph, NetworkXException, has_path,
                      negative_edge_cycle)
from numpy import ndarray


def check(G,
          max_res=None,
          min_res=None,
          REF_forward=None,
          REF_backward=None,
          direction=None,
          algorithm=None):
    """
    Checks whether inputs and the graph are of the appropriate types and
    have the required properties.
    For non-specified REFs, removes nodes that cannot be reached due to
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

    REF_forward, REF_backward : function, optional
        Custom resource extension function. See `REFs`_ for more details.
        Default: additive, subtractive.

    direction : string, optional
        preferred search direction. Either 'both','forward', or, 'backward'.
        Default : 'both'.

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs

    :raises: Raises exceptions if incorrect input is given.
        If multiple exceptions are raised, an exception with a list of
        errors is raised.
    """
    errors = []
    if REF_forward or REF_backward:
        # Cannot apply pruning with custom REFs
        try:
            _check_REFs(REF_forward, REF_backward)
        except Exception as e:
            errors.append(e)
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


def _check_res(G, max_res, min_res, direction, algorithm):
    if isinstance(max_res, list) and isinstance(min_res, list):
        if len(max_res) == len(min_res):
            if (algorithm and 'bidirectional' in algorithm
                    and len(max_res) < 2):
                raise TypeError("Resources must be of length >= 2")
            if (all(isinstance(i, (float, int)) for i in max_res)
                    and all(isinstance(i, (float, int)) for i in min_res)):
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
            raise TypeError("Input graph must have 'n_res' attribute")
    else:
        raise TypeError("Input must be a nx.Digraph()")


def _check_edge_attr(G, max_res, min_res, direction, algorithm):
    """Checks whether edges in input graph have res_cost attribute"""
    if not all('res_cost' in edge[2] for edge in G.edges(data=True)):
        raise TypeError(
            "Input graph must have edges with 'res_cost' attribute")
    if not all(
            len(edge[2]['res_cost']) == G.graph['n_res']
            for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to 'n_res'"
        )
    if not all(
            len(edge[2]['res_cost']) == len(max_res) == len(min_res)
            for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to" +
            " 'min_res' == 'max_res")
    if not all(
            isinstance(edge[2]['res_cost'], ndarray)
            for edge in G.edges(data=True)):
        raise TypeError("The edge 'res_cost' attribute must be a numpy.array")


def _check_path(G, max_res, min_res, direction, algorithm):
    """Checks whether a 'Source' -> 'Sink' path exists and if there are
    negative edge cycles in the graph.
    Also covers nodes missing and other standard networkx exceptions"""
    try:
        if not has_path(G, 'Source', 'Sink'):
            raise NetworkXException("Disconnected Graph")
        if negative_edge_cycle(G):
            raise NetworkXException("A negative cost cycle was found")
    except NetworkXException as e:
        raise Exception("An error occurred: {}".format(e))


def _check_REFs(REF_forward, REF_backward):
    if ((REF_forward and not callable(REF_forward))
            or (REF_backward and not callable(REF_backward))
            or (REF_forward and REF_backward and not callable(REF_forward)
                and not callable(REF_backward))):
        raise TypeError("REF functions must be callable")
