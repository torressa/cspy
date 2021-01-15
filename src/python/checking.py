from time import time
from typing import Union
from logging import getLogger

from networkx import DiGraph, NetworkXException, has_path
from numpy import ndarray
from numpy.random import RandomState

LOG = getLogger(__name__)


def check(G,
          max_res=None,
          min_res=None,
          direction=None,
          REF_callback=None,
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
        :math:`[M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 1`

    min_res : list of floats, optional
        :math:`[L_1, L_2, ..., L_{nres}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 1`

    direction : string, optional
        preferred search direction. Either 'both','forward', or, 'backward'.
        Default : 'both'.

    REF_forward, REF_backward, REF_join : functions, optional
        Custom resource extension function. See `REFs`_ for more details.

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs

    :raises: Raises exceptions if incorrect input is given.
        If multiple exceptions are raised, an exception with a list of
        errors is raised.
    """
    errors = []
    if REF_callback:
        try:
            _check_REF(REF_callback)
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


def check_seed(seed, algorithm=None):
    """Check whether given seed can be used to seed a numpy.random.RandomState
    :return: numpy.random.RandomState (seeded if seed given)
    """
    if algorithm and "bidirectional" in algorithm:
        if not isinstance(seed, int):
            raise TypeError("{} cannot be used to seed".format(seed))
    if seed is None:
        return RandomState()
    elif isinstance(seed, int):
        return RandomState(seed)
    elif isinstance(seed, RandomState):
        return seed
    else:
        raise TypeError("{} cannot be used to seed".format(seed))


def check_time_limit_breached(start_time: float,
                              time_limit: Union[int, None]) -> bool:
    """Check time limit.
    :return: True if difference between current time and start time
    exceeds the time limit. False otherwise.
    """
    if time_limit is not None:
        return time_limit - (time() - start_time) <= 0.0
    return False


def _check_res(G, max_res, min_res, direction, algorithm):
    if isinstance(max_res, list) and isinstance(min_res, list):
        if len(max_res) == len(min_res):
            if not ((all(isinstance(i, (float, int)) for i in max_res) and
                     all(isinstance(i, (float, int)) for i in min_res))):
                raise TypeError("Elements of input lists must be numbers")
        else:
            raise TypeError("Input lists have to be equal length")
    else:
        raise TypeError("Inputs have to be lists")


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
    if any('res_cost' not in edge[2] for edge in G.edges(data=True)):
        raise TypeError("Input graph must have edges with 'res_cost' attribute")
    if any(
            len(edge[2]['res_cost']) != G.graph['n_res']
            for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to 'n_res'")
    if any(not len(edge[2]['res_cost']) == len(max_res) == len(min_res)
           for edge in G.edges(data=True)):
        raise TypeError(
            "Edges must have 'res_cost' attribute with length equal to" +
            " 'min_res' == 'max_res")
    if not all(
            isinstance(edge[2]['res_cost'], ndarray) for edge in G.edges(
                data=True)) and "bidirectional" not in algorithm:
        raise TypeError("The edge 'res_cost' attribute must be a numpy.array")


def _check_path(G, max_res, min_res, direction, algorithm):
    """Checks whether a 'Source' -> 'Sink' path exists and if there are
    negative edge cycles in the graph.
    Also covers nodes missing and other standard networkx exceptions"""
    try:
        if not has_path(G, 'Source', 'Sink'):
            raise NetworkXException("Disconnected Graph")
    except NetworkXException as e:
        raise Exception("An error occurred: {}".format(e))


def _check_REF(REF_callback):
    if REF_callback and not (callable(REF_callback.REF_fwd) or callable(
            REF_callback.REF_bwd) or callable(REF_callback.REF_join)):
        raise TypeError("At least one REF function must be callable")
    if (REF_callback and callable(REF_callback.REF_fwd) and
            callable(REF_callback.REF_bwd) and
            not callable(REF_callback.REF_join)):
        LOG.warning("Default criteria used for joining paths.")
    if (REF_callback and callable(REF_callback.REF_fwd) and
            not callable(REF_callback.REF_bwd) and
            not callable(REF_callback.REF_join)):
        LOG.warning("Forward REF set but not backward REF."
                    " This may lead to unexpected results.")
        LOG.warning("Default criteria used for joining paths.")
