# TODO: write checks for all inputs

from __future__ import absolute_import
from __future__ import print_function

import logging
import numpy as np
from math import factorial
from random import sample, randint
from itertools import permutations
# from networkx import astar_path, NetworkXException
from cspy.preprocessing import check
from cspy.path import Path

log = logging.getLogger(__name__)


class GRASP:
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

    max_iter : int
        Maximum number of iterations for algorithm

    max_localiter : int
        Maximum number of local search iterations

    alpha : float, optional
        Greediness factor 0 (random) --> 1 (greedy)

    Returns
    -------
    path : list
        nodes in resource feasible shortest path obtained.

    Raises
    ------
    Exception
        if no resource feasible path is found

    Notes
    -----
    The input graph must have a ``n_res`` attribute.
    The edges in the graph must all have a ``res_cost`` attribute.
    Also, we must have ``len(min_res)`` :math:`=` ``len(max_res)``.
    See `Using cspy`_

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html


    Example
    -------
    To run the algorithm, create a :class:`GRASP` instance and call `run`.

    .. code-block:: python

        >>> from cspy import GRASP
        >>> from networkx import DiGraph
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=[1, 1], weight=1)
        >>> G.add_edge('Source', 'B', res_cost=[1, 1], weight=1)
        >>> G.add_edge('Source', 'C', res_cost=[10, 1], weight=10)
        >>> G.add_edge('A', 'C', res_cost=[1, 1], weight=1)
        >>> G.add_edge('A', 'E', res_cost=[10, 1], weight=10)
        >>> G.add_edge('A', 'F', res_cost=[10, 1], weight=10)
        >>> G.add_edge('B', 'C', res_cost=[2, 1], weight=-1)
        >>> G.add_edge('B', 'F', res_cost=[10, 1], weight=10)
        >>> G.add_edge('B', 'E', res_cost=[10, 1], weight=10)
        >>> G.add_edge('C', 'D', res_cost=[1, 1], weight=-1)
        >>> G.add_edge('D', 'E', res_cost=[1, 1], weight=1)
        >>> G.add_edge('D', 'F', res_cost=[1, 1], weight=1)
        >>> G.add_edge('D', 'Sink', res_cost=[10, 10], weight=10)
        >>> G.add_edge('F', 'Sink', res_cost=[10, 1], weight=1)
        >>> G.add_edge('E', 'Sink', res_cost=[1, 1], weight=1)
        >>> path = GRASP(G, [5, 5], [0, 0], 50, 10).run()
        >>> print(path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']

    .. _Ferone et al 2019: https://www.tandfonline.com/doi/full/10.1080/10556788.2018.1548015

    """

    def __init__(self, G, max_res, min_res, max_iter, max_localiter, alpha=0.9):
        # Check input graph and parameters
        check(G, max_res, min_res)
        # Input parameters
        self.G = G
        self.max_res = max_res
        self.min_res = min_res
        self.max_iter = max_iter
        self.max_localiter = max_localiter
        self.alpha = alpha
        # Algorithm specific parameters
        self.it = 0
        self.best = None
        self.stop = False
        self.nodes = self.G.nodes()

    def run(self):
        while self.it < self.max_iter and not self.stop:
            self.algorithm()
            self.it += 1
        if self.best.path:
            return self.best.path
        else:
            raise Exception("No resource feasible path has been found")

    def algorithm(self):
        solution = self._construct()
        solution = self._local_search(solution)
        self._update_best(solution)

    def _construct(self):
        solution = Solution(sample(self.nodes, 1), 0)  # Init solution
        # Construction phase
        while len(solution.path) < len(self.nodes):
            candidates = [i for i in self.nodes if i not in solution.path]
            weights = [
                self._heuristic(solution.path[-1], i) for i in candidates
            ]
            # Build Restricted Candidiate List (RCL)
            restriced_candidates = [
                candidates[i]
                for i, c in enumerate(weights)
                if c <= (min(weights) + self.alpha *
                         (max(weights) - min(weights)))
            ]
            # Select random node from RCL to add to the current solution
            solution.path.append(np.random.choice(restriced_candidates))
            solution.cost = self._cost_solution(solution)
        return solution

    def _local_search(self, solution):
        it = 0  # init local iteration counter
        while it < self.max_localiter:  # Local search phase
            # Init candidate solution using random valid path generator
            candidate = Solution(
                self._find_alternative_paths(self.G, solution.path), 0)
            # evaluate candidate solution
            candidate.cost = self._cost_solution(candidate)
            # Update solution with candidate if lower cost and resource feasible
            if (candidate.path and candidate.cost < solution.cost and
                    self._check_path(candidate)):
                solution = candidate
            it += 1
        return solution

    def _update_best(self, solution):
        if not self.best or solution.cost < self.best.cost:
            self.best = solution

    def _heuristic(self, i, j):
        # Given a node pair returns a weight to apply
        if i and j:
            if (i, j) not in self.G.edges():
                return 1e10
            else:
                return self.G.get_edge_data(i, j)['weight']
        else:
            return 1e10

    @staticmethod
    def _find_alternative_paths(G, path):
        """ Static Method used in local search to randomly generate valid paths.
        Using a subset of edges, it generates a connected path starting at
        the source node. """
        n_permutations = int(factorial(len(path)) / factorial(len(path) - 2))
        sample_size = randint(int(n_permutations / 2), n_permutations)
        selection = sample(list(permutations(path, 2)), sample_size)
        path_edges = dict(list(edge for edge in selection if edge in G.edges()))
        elem = 'Source'  # start point in the new list
        new_list = []
        for _ in range(len(path_edges)):
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
        return nodes_to_keep

    def _cost_solution(self, solution=None):
        if solution:
            return sum(
                self._heuristic(i, j)
                for i, j in zip(solution.path, solution.path[1:]))
        else:
            return 1e11

    def _check_path(self, solution=None):
        """
        Returns True if solution.path is valid and resource feasible,
        False otherwise
        """
        if solution:
            path, cost = solution.path, solution.cost
            if (len(path) > 2 and cost < 1e10 and path[0] == 'Source' and
                    path[-1] == 'Sink'):
                if Path(self.G, path, self.max_res,
                        self.min_res)._check_feasibility() is True:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False


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

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "Solution({0},{1})".format(self.path, self.cost)
