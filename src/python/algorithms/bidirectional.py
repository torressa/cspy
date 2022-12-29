# Wrapper for BiDirectionalCpp
from typing import List, Optional, Tuple, Union

from networkx import DiGraph, convert_node_labels_to_integers, get_node_attributes
from cspy.preprocessing import preprocess_graph
from cspy.checking import check

# Import from the SWIG output file
from .pyBiDirectionalCpp import BiDirectionalCpp, REFCallback, DoubleVector


class BiDirectional:
    """
    Python wrapper for the bidirectional labelling algorithm with dynamic
    half-way point (`Tilk 2017`_).

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    max_res : list of floats
        :math:`[H_F, M_1, M_2, ..., M_{n\_res}]` upper bounds for resource
        usage (including initial forward stopping point).
        We must have ``len(max_res)`` :math:`=` ``len(max_res)``

    min_res : list of floats
        :math:`[H_B, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource
        usage (including initial backward stopping point).
        We must have ``len(min_res)`` :math:`=` ``len(max_res)``

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    direction : string, optional
        preferred search direction.
        Either "both", "forward", or, "backward". Default : "both".

    method : string, optional
        preferred method for determining search direction.
        Either "generated" (direction with least number of generated
        labels), "processed" (direction with least number of processed labels),
        or, "unprocessed" (direction with least number of unprocessed labels).
        Default: "unprocessed"

    time_limit : float or int, optional
        time limit in seconds.
        Default: None

    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path with
        total cost <= threshold.
        Note this typically causes the search to terminate early.
        Default: None

    elementary : bool, optional
        whether the problem is elementary. i.e. no cycles are allowed in the
        final path. Note, True increases run time.
        Default: False

    bounds_pruning : bool, optional
        whether lower bounds based on shortest paths are used when pruning labels
        using primal bounds.
        Note this is an experimental feature. See issues.
        Default: False

    find_critical_res : bool, optional
        bool with whether critical resource is found at the preprocessing stage.
        Note1: this is an experimental feature. See issues.
        Note2: overrides critical_res value.
        Default false.

    critical_res : int, optional
        Resource index to use as primary resource. Note: corresponding resource
        has to fulfil some conditions (e.g. monotonicity). See `REFs`_.
        Default: 0

    seed : None or int, optional
        *Disabled*
        seed for random method class. Default : None.

    REF_callback : REFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    two_cycle_elimination: bool, optional
        whether 2-cycles should be eliminated for non-elementary RCSPP

    .. _REFs : https://cspy.readthedocs.io/en/latest/ref.html
    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
    """

    def __init__(
        self,
        G: DiGraph,
        max_res: List[float],
        min_res: List[float],
        preprocess: Optional[bool] = False,
        direction: Optional[str] = "both",
        method: Optional[str] = "unprocessed",
        time_limit: Optional[Union[float, int]] = None,
        threshold: Optional[float] = None,
        elementary: Optional[bool] = False,
        bounds_pruning: Optional[bool] = False,
        find_critical_res: Optional[bool] = False,
        critical_res: Optional[int] = None,
        # seed: Union[int] = None,
        REF_callback: Optional[REFCallback] = None,
        two_cycle_elimination: Optional[bool] = False,
    ):
        # Check inputs
        check(G, max_res, min_res, direction, REF_callback, __name__)
        # check_seed(seed, __name__)
        # Preprocess and save graph
        self.G: DiGraph = preprocess_graph(
            G, max_res, min_res, preprocess, REF_callback
        )
        # Dictionary with graph label -> original label
        self._original_node_labels = None
        # Vertex id with source/sink
        self._source_id: int = None
        self._sink_id: int = None

        max_res_vector = _list_to_double_vector(max_res)
        min_res_vector = _list_to_double_vector(min_res)

        # Pass graph
        self._init_graph()
        self.bidirectional_cpp = BiDirectionalCpp(
            len(self.G.nodes()),
            len(self.G.edges()),
            self._source_id,
            self._sink_id,
            max_res_vector,
            min_res_vector,
        )
        self._load_graph()
        # pass solving attributes
        if direction != "both":
            self.bidirectional_cpp.setDirection(direction)
        if method in ["random", "generated", "processed"]:
            self.bidirectional_cpp.setMethod(method)
        if time_limit is not None and isinstance(time_limit, (int, float)):
            self.bidirectional_cpp.setTimeLimit(time_limit)
        if threshold is not None and isinstance(threshold, (int, float)):
            self.bidirectional_cpp.setThreshold(threshold)
        if isinstance(elementary, bool) and elementary:
            self.bidirectional_cpp.setElementary(True)
        if isinstance(bounds_pruning, bool) and not bounds_pruning:
            self.bidirectional_cpp.setBoundsPruning(bounds_pruning)
        if isinstance(find_critical_res, bool) and find_critical_res:
            self.bidirectional_cpp.setFindCriticalRes(True)
        if isinstance(critical_res, int) and critical_res != 0:
            self.bidirectional_cpp.setCriticalRes(critical_res)
        if REF_callback is not None:
            # Add a Python callback (caller owns the callback, so we
            # disown it first by calling __disown__).
            # see: https://github.com/swig/swig/blob/b6c2438d7d7aac5711376a106a156200b7ff1056/Examples/python/callback/runme.py#L36
            self.bidirectional_cpp.setREFCallback(REF_callback)
        # if isinstance(seed, int) and seed is not None:
        #     self.bidirectional_cpp.setSeed(seed)
        if isinstance(two_cycle_elimination, bool) and two_cycle_elimination:
            self.bidirectional_cpp.setTwoCycleElimination(True)

    def run(self):
        "Run the algorithm in series"
        self.bidirectional_cpp.run()

    def run_parallel(self):
        "Run the algorithm in parallel"
        raise NotImplementedError("Coming soon")

    @property
    def path(self):
        """Get list with nodes in calculated path."""
        path = self.bidirectional_cpp.getPath()
        # format as list on return as SWIG returns "tuple"
        if len(path) <= 0:
            return None
        return [self.G.nodes[p]["original_label"] for p in path]

    @property
    def total_cost(self):
        """Get accumulated cost along the path."""
        path = self.bidirectional_cpp.getPath()
        return self.bidirectional_cpp.getTotalCost() if len(path) > 0 else None

    @property
    def consumed_resources(self):
        """Get accumulated resources consumed along the path."""
        path = self.bidirectional_cpp.getPath()
        res = self.bidirectional_cpp.getConsumedResources()
        if len(path) > 0 and len(res) > 0:
            return list(res)
        else:
            return None

    def check_critical_res(self):
        """After running the algorithm, one can check if critical resource is
        tight (difference between final resource and maximum) and prints a
        message if it doesn't match to the one chosen (or default one).
        """
        self.bidirectional_cpp.checkCriticalRes()

    def _init_graph(self):
        # Convert node label to integers and saves original labels in
        # new node attribute "original_label"
        self.G = convert_node_labels_to_integers(
            self.G, label_attribute="original_label"
        )
        self._original_node_labels = get_node_attributes(self.G, "original_label")
        # Save source and sink node ids (integers)
        self._source_id = self._get_original_node_label("Source")
        self._sink_id = self._get_original_node_label("Sink")

    def _load_graph(self):
        # Load nodes
        self.bidirectional_cpp.addNodes(list(self.G.nodes()))
        # Load each edge independently
        for edge in self.G.edges(data=True):
            res_cost = _list_to_double_vector(edge[2]["res_cost"])
            self.bidirectional_cpp.addEdge(
                edge[0], edge[1], edge[2]["weight"], res_cost
            )

    def _get_original_node_label(self, node_label):
        matching_labels = [
            k for k, v in self._original_node_labels.items() if v == node_label
        ]
        if len(matching_labels) == 1:
            return matching_labels[0]
        else:
            raise Exception("Node label not found")


def _list_of_tuple_to_int_pair_vector(input_list: List[Tuple[int, int]]):
    int_pair_vector = IntPairVector()
    for (elem1, elem2) in input_list:
        int_pair_vector.append(IntPair(elem1, elem2))
    return int_pair_vector


def _list_to_double_vector(input_list: List[float]):
    double_vector = DoubleVector()
    for elem in input_list:
        double_vector.append(float(elem))
    return double_vector
