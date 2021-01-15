from time import time
from logging import getLogger
from typing import List, Optional, Callable

from numpy import array
from networkx import NetworkXException, DiGraph

# Local imports
from cspy.algorithms.path_base import PathBase
from cspy.checking import check_time_limit_breached

log = getLogger(__name__)


class GreedyElim(PathBase):
    """
    Simple Greedy elimination algorithm for the (resource) constrained shortest
    path problem. The algorithms solves a standard shortest path problem and
    eliminates resource infeasible edges iteratively until a resource feasible
    path is found.

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    max_res : list of floats
        :math:`[M_1, M_2, ..., M_{n\_res}]` upper bounds for resource
        usage (including initial forward stopping point).

    min_res : list of floats
        :math:`[L_1, L_2, ..., L_{n\_res}]` lower bounds for resource
        usage (including initial backward stopping point).
        We must have ``len(min_res)`` :math:`=` ``len(max_res)``.

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    algorithm : string, optional
        shortest path algorithm to use. Options are "`simple`_"
        or "`astar`_".
        If the input network has a negative cycle, the "`simple`_"
        algorithm is automatically chosen (as the astar algorithm cannot cope).

    max_depth : int, optional
        depth for search of shortest simple path. Default : 1000.
        If the total number of simple paths is less than max_depth,
        then the shortest path is used.

    time_limit : int, optional
        time limit in seconds.
        Default: None

    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path with
        total cost <= threshold.
        Note this typically causes the search to terminate early.
        Default: None

    REF_callback : REFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    .. _REFs : https://cspy.readthedocs.io/en/latest/ref.html
    .. _simple : https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.shortest_simple_paths.html#networkx.algorithms.simple_paths.shortest_simple_paths
    .. _astar : https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html#networkx.algorithms.shortest_paths.astar.astar_path

    Raises
    ------
    Exception
        if no resource feasible path is found
    """

    def __init__(self,
                 G: DiGraph,
                 max_res: List,
                 min_res: List,
                 preprocess: Optional[bool] = False,
                 algorithm: Optional[str] = "simple",
                 max_depth: Optional[int] = 1000,
                 time_limit: Optional[int] = None,
                 threshold: Optional[float] = None,
                 REF_callback=None):
        # Pass arguments to parent class
        super().__init__(G, max_res, min_res, preprocess, threshold,
                         REF_callback, algorithm)
        # Algorithm specific parameters
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.stop = False
        self.predecessor_edges = []
        self.last_edge_removed = None
        self.edges_to_remove = dict(self.G.edges())
        # To return
        self.best_path = []

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        start = time()
        while not self.stop and not check_time_limit_breached(
                start, self.time_limit):
            self._algorithm()

        if not self.best_path:
            raise Exception("No resource feasible path has been found")

    def _algorithm(self):
        path = []
        try:
            path = self.get_shortest_path("Source", self.max_depth)
        except NetworkXException:
            pass
        if path:
            # Set PathBase attribute
            self.st_path = path
            edge_or_true = self.check_feasibility()
            if edge_or_true is True:
                self.stop = True
            else:
                self.remove_edge(edge_or_true)
                self.last_edge_removed = edge_or_true
        else:
            # no path has been found for current graph
            # Add previously removed edge
            self.add_edge_back(self.last_edge_removed)
            # Remove a predecessor edge instead
            self.remove_edge(self._get_predecessor_edges(
                self.last_edge_removed))

    def _get_predecessor_edges(self, edge):
        if not self.predecessor_edges:
            node = edge[0]
            if node == "Source":
                self.stop = True
                return edge
            self.predecessor_edges = [
                e for e in self.G.edges(self.G.nbunch_iter(
                    [node] + list(self.G.predecessors(node))),
                                        data=True) if e[1] == node and e != edge
            ]
            self.predecessor_edges.sort(key=lambda x: x[2]['weight'])
        next_edge = self.predecessor_edges[-1]
        self.predecessor_edges.pop(-1)
        return next_edge

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])
