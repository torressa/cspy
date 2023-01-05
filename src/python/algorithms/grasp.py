from time import time
from itertools import repeat
from logging import getLogger
from collections import deque
from typing import List, Optional
from random import sample, randint

from networkx import DiGraph
from numpy.random import choice
import numpy as np

# Local imports
from cspy.algorithms.path_base import PathBase
from cspy.checking import check_time_limit_breached

log = getLogger(__name__)


class GRASP(PathBase):
    """
    Greedy Randomised Adaptive Search Procedure for the (resource) constrained
    shortest path problem. Adapted from `Ferone et al 2019`_.

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute. Also, the number of nodes must be
        :math:`\geq 5`.

    max_res : list of floats
        :math:`[M_1, M_2, ..., M_{n\_res}]` upper bounds for resource
        usage.

    min_res : list of floats
        :math:`[L_1, L_2, ..., L_{n\_res}]` lower bounds for resource
        usage.

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    max_iter : int, optional
        Maximum number of iterations for algorithm. Default : 100.

    max_localiter : int, optional
        Maximum number of local search iterations. Default : 10.

    time_limit : int, optional
        time limit in seconds.
        Default: None

    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path with
        total cost <= threshold.
        Note this typically causes the search to terminate early.
        Default: None

    alpha : float, optional
        Greediness factor 0 (random) --> 1 (greedy). Default : 0.2.

    REF_callback : REFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    .. _REFs : https://cspy.readthedocs.io/en/latest/ref.html
    .. _Ferone et al 2019: https://www.tandfonline.com/doi/full/10.1080/10556788.2018.1548015

    Raises
    ------
    Exception
        if no resource feasible path is found

    """

    def __init__(
        self,
        G: DiGraph,
        max_res: List[float],
        min_res: List[float],
        preprocess: Optional[bool] = False,
        max_iter: Optional[int] = 100,
        max_localiter: Optional[int] = 10,
        time_limit: Optional[int] = None,
        threshold: Optional[float] = None,
        alpha: Optional[float] = 0.2,
        REF_callback=None,
    ):
        # Pass arguments to parent class
        super().__init__(G, max_res, min_res, preprocess, threshold, REF_callback)
        # Algorithm specific attributes
        self.max_iter = max_iter
        self.max_localiter = max_localiter
        self.time_limit = time_limit
        self.alpha = alpha
        # Algorithm specific parameters
        self.it = 0
        self.stop = False
        self.best_path = None
        self.best_solution = None
        self.nodes = sorted(list(self.G.nodes()))

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        start = time()
        while (
            self.it < self.max_iter
            and not self.stop
            and not check_time_limit_breached(start, self.time_limit)
        ):
            self._algorithm()
            self.it += 1
        if not self.best_solution.path:
            raise Exception("No resource feasible path has been found")

    def _algorithm(self):
        solution = self._construct()
        solution = self._local_search(solution)
        self._update_best(solution)

    def _construct(self):
        solution = Solution(sample(self.nodes, 1), 0)  # Init solution
        # Construction phase
        while len(solution.path) < len(self.nodes):
            candidates = [i for i in self.nodes if i not in solution.path]
            weights = deque(map(self._heuristic, repeat(solution.path[-1]), candidates))
            # Build Restricted Candidiate List (RCL)
            restriced_candidates = [
                candidates[i]
                for i, c in enumerate(weights)
                if c <= (min(weights) + self.alpha * (max(weights) - min(weights)))
            ]
            # Select random node from RCL to add to the current solution
            solution.path.append(choice(restriced_candidates))
            solution.cost = self._cost_solution(solution)
        return solution

    def _local_search(self, solution):
        for _ in range(self.max_localiter):  # Local search phase
            # Init candidate solution using random valid path generator
            candidate = Solution(self._find_alternative_paths(self.G, solution.path), 0)
            # evaluate candidate solution
            candidate.cost = self._cost_solution(candidate)
            # Update solution with candidate if lower cost and resource feasible
            if (
                candidate.path
                and candidate.cost < solution.cost
                and self._check_path(candidate)
            ):
                solution = candidate
        return solution

    def _update_best(self, solution):
        if not self.best_solution or solution.cost < self.best_solution.cost:
            self.best_solution = solution

    def _heuristic(self, i, j):
        # Given a node pair returns a weight to apply
        if i and j:
            if (i, j) not in self.G.edges():
                return 1e10
            else:
                return self.G.get_edge_data(i, j)["weight"]
        else:
            return 1e10

    def _cost_solution(self, solution=None):
        if solution:
            return sum(
                self._heuristic(i, j) for i, j in zip(solution.path, solution.path[1:])
            )
        else:
            return 1e11

    def _check_path(self, solution=None):
        """
        Returns True if solution.path is valid and resource feasible,
        False otherwise
        """
        if solution:
            path, cost = solution.path, solution.cost
            if (
                len(path) > 2
                and cost < 1e10
                and path[0] == "Source"
                and path[-1] == "Sink"
            ):
                self.st_path = path
                return self.check_feasibility(return_edge=False)
            else:
                return False
        else:
            return False

    @staticmethod
    def _find_alternative_paths(G, path, rng=None):
        """
        Static Method used in local search to randomly generate valid paths.
        Using a subset of edges, it generates a connected path starting at
        the source node.
        """
        # get all edges involving only these nodes
        poss_edges = G.subgraph(path).edges()
        if poss_edges:
            sample_size = randint(1, len(poss_edges))
            if rng:
                tmp = np.empty(len(poss_edges), dtype="object")
                tmp[:] = poss_edges
                selection = rng.choice(tmp, replace=False, size=sample_size).tolist()
            else:
                selection = sample(deque(poss_edges), sample_size)
            # will use last value tried with given key
            path_edges = dict([edge for edge in selection if edge in G.edges()])
            elem = "Source"  # start point in the new list
            new_list = []
            for _ in path_edges:
                try:
                    new_list.append((elem, path_edges[elem]))
                    elem = path_edges[elem]
                except KeyError:
                    pass
            if new_list:
                nodes_to_keep = [t[0] for t in new_list]
                nodes_to_keep.append(new_list[-1][1])
            else:
                nodes_to_keep = []
        else:
            nodes_to_keep = []
        return nodes_to_keep


class Solution(object):
    """
    Object for solutions and candidates during GRASP iterations.

    Parameters
    ----------

    path : list
        list of nodes in current path

    cost : float
        cost of solution
    """

    def __init__(self, path, cost):
        self.path = path
        self.cost = cost
