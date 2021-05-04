# Wrapper for BiDirectionalCpp
from typing import List, Optional, Union

from networkx import DiGraph, convert_node_labels_to_integers
from numpy.random import RandomState

from cspy.preprocessing import preprocess_graph
from cspy.checking import check, check_seed

# Import from the SWIG output file
from .pyBiDirectionalCpp import BiDirectionalCpp, REFCallback, DoubleVector


class BiDirectional:
    """
    Implementation of the bidirectional labelling algorithm with dynamic
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
        Note this is an experimental feauture. See issues.
        Default: False

    seed : None or int, optional
        seed for random method class. Default : None.

    REF_callback : REFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    .. _REFs : https://cspy.readthedocs.io/en/latest/ref.html
    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
    """

    def __init__(self,
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
                 seed: Union[int] = None,
                 REF_callback: Optional[REFCallback] = None):
        # Check inputs
        check(G, max_res, min_res, direction, REF_callback, __name__)
        # check_seed(seed, __name__)
        # Preprocess and save graph
        self.G: DiGraph = preprocess_graph(G, max_res, min_res, preprocess,
                                           REF_callback)
        # Vertex id with source/sink
        self._source_id: int = None
        self._sink_id: int = None

        max_res_vector = _convert_list_to_double_vector(max_res)
        min_res_vector = _convert_list_to_double_vector(min_res)

        # Pass graph
        self._init_graph()
        self.bidirectional_cpp = BiDirectionalCpp(len(self.G.nodes()),
                                                  len(self.G.edges()),
                                                  self._source_id,
                                                  self._sink_id, max_res_vector,
                                                  min_res_vector)
        self._load_graph()
        # pass solving attributes
        if direction != "both":
            self.bidirectional_cpp.options.direction = direction
        if method in ["random", "generated", "processed"]:
            self.bidirectional_cpp.options.method = method
        if time_limit is not None and isinstance(time_limit, (int, float)):
            self.bidirectional_cpp.options.time_limit = time_limit
        if threshold is not None and isinstance(time_limit, (int, float)):
            self.bidirectional_cpp.options.threshold = threshold
        if isinstance(elementary, bool) and elementary:
            self.bidirectional_cpp.options.elementary = elementary
        if isinstance(bounds_pruning, bool) and not bounds_pruning:
            self.bidirectional_cpp.options.bounds_pruning = bounds_pruning
        if isinstance(seed, int) and seed is not None:
            self.bidirectional_cpp.setSeed(seed)
        if REF_callback is not None:
            # Add a Python callback (caller owns the callback, so we
            # disown it first by calling __disown__).
            # see: https://github.com/swig/swig/blob/b6c2438d7d7aac5711376a106a156200b7ff1056/Examples/python/callback/runme.py#L36
            self.bidirectional_cpp.setREFCallback(REF_callback.__disown__())

    def run(self):
        'Run the algorithm in series'
        self.bidirectional_cpp.run()

    def run_parallel(self):
        'Run the algorithm in parallel'
        # self.bidirectional_cpp.run_parallel()
        raise NotImplementedError("Coming soon")

    @property
    def path(self):
        """Get list with nodes in calculated path.
        """
        path = self.bidirectional_cpp.getPath()
        # format as list on return as SWIG returns "tuple"
        if len(path) <= 0:
            return None

        _path = []
        # Convert path to original labels and return
        for p in path:
            _path.append(self.G.nodes[p]["original_label"])
        return _path

    @property
    def total_cost(self):
        """Get accumulated cost along the path.
        """
        path = self.bidirectional_cpp.getPath()
        return self.bidirectional_cpp.getTotalCost() if len(path) > 0 else None

    @property
    def consumed_resources(self):
        """Get accumulated resources consumed along the path.
        """
        path = self.bidirectional_cpp.getPath()
        res = self.bidirectional_cpp.getConsumedResources()
        if (len(path) > 0 and len(res) > 0):
            return list(res)
        else:
            return None

    def _init_graph(self):
        # Convert node label to integers and saves original labels in
        # new node attribute "original_label"
        self.G = convert_node_labels_to_integers(
            self.G, label_attribute="original_label")
        # Save source and sink node ids (integers)
        self._source_id = [
            n for n in self.G.nodes()
            if self.G.nodes[n]["original_label"] == "Source"
        ][0]
        self._sink_id = [
            n for n in self.G.nodes()
            if self.G.nodes[n]["original_label"] == "Sink"
        ][0]

    def _load_graph(self):
        # Load nodes
        self.bidirectional_cpp.addNodes(list(self.G.nodes()))
        # Load each edge independently
        for edge in self.G.edges(data=True):
            res_cost = _convert_list_to_double_vector(edge[2]["res_cost"])
            self.bidirectional_cpp.addEdge(edge[0], edge[1], edge[2]["weight"],
                                           res_cost)


def _convert_list_to_double_vector(input_list: List[float]):
    double_vector = DoubleVector()
    for elem in input_list:
        double_vector.append(float(elem))
    return double_vector
