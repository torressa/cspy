from time import time
from logging import getLogger
from typing import List, Optional, Callable
from collections import deque

from networkx import NetworkXException, DiGraph

# Local imports
from cspy.algorithms.path_base import PathBase
from cspy.checking import check_time_limit_breached

log = getLogger(__name__)


class Tabu(PathBase):
    """
    Simple Tabu-esque algorithm for the (resource) constrained shortest
    path problem.

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
                 max_res: List[float],
                 min_res: List[float],
                 preprocess: Optional[bool] = False,
                 algorithm: Optional[str] = "simple",
                 max_depth: Optional[int] = 1000,
                 time_limit: Optional[int] = None,
                 threshold: Optional[float] = None,
                 REF_callback: Callable = None):
        # Pass arguments to PathBase object
        super().__init__(G, max_res, min_res, preprocess, threshold,
                         REF_callback, algorithm)
        # Algorithm specific parameters
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.iteration = 0
        self.stop = False
        self.neighbour = 'Source'
        self.neighbourhood = []
        self.tabu_edge = None
        self.edges_to_check = dict(self.G.edges())

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        start = time()
        while not self.stop and not check_time_limit_breached(
                start, self.time_limit):
            self._algorithm()
            self.iteration += 1

        if not self.best_path:
            raise Exception("No resource feasible path has been found")

    def _algorithm(self):
        path = []
        try:
            path = self.get_shortest_path(self.neighbour, self.max_depth)
        except NetworkXException:
            pass
        if path:
            self._update_path(self.neighbour, path)
            edge_or_true = self.check_feasibility()
            # If there is a resource feasible path
            if edge_or_true is True:
                self.stop = True
            # Otherwise, use the infeasible edge as the next tabu edge
            else:
                self._get_neighbour(edge_or_true)
        else:
            log.debug("No path found")
            self._get_neighbour(self.tabu_edge)

    # Path-related methods #
    def _update_path(self, neighbour, path):
        # Joins path using previous path and [neighbour, ..., sink] path
        if neighbour == "Source":
            self.st_path = path
        elif neighbour in self.st_path:
            # Paths can be joined at neighbour
            self.st_path = [
                node for node in self.st_path
                if (node != neighbour and
                    self.st_path.index(node) < self.st_path.index(neighbour))
            ] + path
        else:
            self._merge_paths(neighbour, path)

    def _merge_paths(self, neighbour, path):
        branch_path = [n for n in self.st_path if n not in path]
        for node in reversed(branch_path):
            if (node, neighbour) in self.G.edges():
                self.st_path = [
                    n for n in branch_path
                    if (branch_path.index(n) <= branch_path.index(node))
                ] + path
                break

    # Algorithm-specific methods #
    def _update_tabu_edge(self, edge):
        # If a tabu edge has already been selected
        if self.tabu_edge:
            # Revert old tabu edge weight to original
            self.add_edge_back(self.tabu_edge)
        # Replace new tabu edge weight with large number
        self.remove_edge(edge)
        self.tabu_edge = edge

    def _get_neighbour(self, edge=None):
        """
        Get next neighbour to the resource infeasible edge.
        Update the tabu edge.
        """
        if self.edges_to_check:
            if edge and edge[:2] in self.edges_to_check:
                # If edge not already been seen
                current_edge = edge
            else:
                current_edge = self._get_next_neighbour_edge(self.tabu_edge)
        else:
            self.stop = True
            return
        self.edges_to_check.pop(current_edge[:2], None)
        self.neighbour = current_edge[0]
        self._update_tabu_edge(current_edge)

    def _get_next_neighbour_edge(self, edge):
        # Retrieves the edge adjacent to node with the greatest weight
        # If neighbourhood doesn't exist
        if not self.neighbourhood:
            node = edge[0]
            if node == "Source":
                self.stop = True
                return edge
            else:
                nodes_iter = self.G.predecessors(node)
                self.neighbourhood = deque(e for e in self.G.edges(
                    self.G.nbunch_iter(nodes_iter), data=True)
                                           if e[1] == node and e != edge)
        # Get the edge in the neighbourhood with greatest weight
        next_edge = max(self.neighbourhood, key=lambda x: x[2]['weight'])
        # delete edge from neighbourhood
        del self.neighbourhood[self.neighbourhood.index(next_edge)]
        return next_edge
