from typing import List, Optional, Union

from networkx import DiGraph
from numpy.random import RandomState

from cspy.preprocessing import preprocess_graph
from cspy.checking import check, check_seed

# Import from python Cpp wrapper
from pyBiDirectionalCpp import (BiDirectionalCpp, PyREFCallback, DoubleVector)


class BiDirectional:
    """Implementation of the bidirectional labeling algorithm with dynamic
    half-way point (`Tilk 2017`_).
    Depending on the range of values for bounds for the first resource, we get
    four different algorithms. See ``self.name_algorithm`` and Notes.
    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.
    max_res : list of floats
        :math:`[H_F, M_1, M_2, ..., M_{n\_res}]` upper bounds for resource
        usage (including initial forward stopping point).
        We must have ``len(max_res)`` :math:`\geq 2`.
    min_res : list of floats
        :math:`[H_B, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource
        usage (including initial backward stopping point).
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`
    preprocess : bool, optional
        enables preprocessing routine. Default : False.
    direction : string, optional
        preferred search direction.
        Either "both", "forward", or, "backward". Default : "both".
    method : string, optional
        preferred method for determining search direction.
        Either "random", "generated" (direction with least number of generated
        labels), "processed" (direction with least number of processed labels),
        or, "unprocessed" (direction with least number of unprocessed labels).
        Default: "random"
    time_limit : int, optional
        time limit in seconds.
        Default: None
    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path with
        total cost <= threshold.
        Note this typically causes the search to terminate early.
        Default: None
    elementary : bool, optional
        whether the problem is elementary. i.e. no cycles are allowed in the
        final path. Note this may increase run time.
        Default: False
    dominance_frequency : int, optional
        multiple of iterations to run the dominance checks.
        Default : 1 (every iteration)
    seed : None or int or numpy.random.RandomState instance, optional
        seed for PSOLGENT class. Default : None (which gives a single value
        numpy.random.RandomState).
    REF_callback : PyREFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs
    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
    """

    def __init__(self,
                 G: DiGraph,
                 max_res: List[float],
                 min_res: List[float],
                 preprocess: Optional[bool] = False,
                 direction: Optional[str] = "both",
                 method: Optional[str] = "random",
                 time_limit: Optional[float] = 0,
                 threshold: Optional[float] = 0.0,
                 elementary: Optional[bool] = False,
                 dominance_frequency: Optional[int] = 1,
                 seed: Union[int, RandomState, None] = 0,
                 REF_callback: Optional[PyREFCallback] = None):
        # Check inputs
        check(G, max_res, min_res, direction, REF_callback, __name__)
        # Preprocess graph
        G = preprocess_graph(G, max_res, min_res, preprocess, REF_callback)
        check_seed(seed, __name__)

        max_res_vector = _convert_list_to_double_vector(max_res)
        min_res_vector = _convert_list_to_double_vector(min_res)

        self.bidirectional_cpp = BiDirectionalCpp(max_res_vector,
                                                  min_res_vector)
        self._init_graph(G)
        if REF_callback is not None:
            self.bidirectional_cpp.setPyCallback(REF_callback)
        self.bidirectional_cpp.call()

    def run(self):
        'Run the algorithm in series'
        self.bidirectional_cpp.run()

    def run_parallel(self):
        'Run the algorithm in parallel'
        self.bidirectional_cpp.run_parallel()

    @property
    def path(self):
        """Get list with nodes in calculated path.
        """
        path = self.bidirectional_cpp.getPath()
        return path if len(path) > 0 else None

    @property
    def total_cost(self):
        """Get accumulated cost along the path.
        """
        path = self.bidirectional_cpp.getPath()
        return (self.bidirectional_cpp.getTotalCost()
                if len(path) > 0 else None)

    @property
    def consumed_resources(self):
        """Get accumulated resources consumed along the path.
        """
        path = self.bidirectional_cpp.getPath()
        return (self.bidirectional_cpp.getConsumedResources()
                if len(path) > 0 else None)

    def _init_graph(self, G):
        for edge in G.edges(data=True):
            res_cost = _convert_list_to_double_vector(edge[2]["res_cost"])
            self.bidirectional_cpp.addEdge(str(edge[0]), str(edge[1]),
                                           edge[2]["weight"], res_cost)


def _convert_list_to_double_vector(input_list: List[float]):
    double_vector = DoubleVector()
    for elem in input_list:
        double_vector.append(float(elem))
    return double_vector
