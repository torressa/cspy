"""
Adapted from https://github.com/100/Solid/blob/master/Solid/ParticleSwarm.py
"""
from time import time
from math import sqrt
from abc import ABCMeta
from logging import getLogger
from typing import List, Optional, Callable

from networkx import DiGraph
from numpy.random import RandomState
import numpy as np

# Local imports
from cspy.algorithms.grasp import Solution
from cspy.algorithms.path_base import PathBase
from cspy.checking import check_seed, check_time_limit_breached

log = getLogger(__name__)


class PSOLGENT(PathBase):
    """
    Particle Swarm Optimization with combined Local and Global Expanding
    Neighborhood Topology (PSOLGENT) algorithm for the (resource)
    constrained shortest path problem (`Marinakis et al 2017`_).

    Note. Neighborhood expansion not implemented yet, so PSOLGNT.

    Given the nature of our problem we have set the default parameters of
    the algorithm as suggested in the paper mentioned.

    Code adapted from `Solid`_.

    .. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/abs/pii/S0377221717302357

    .. _Solid: https://github.com/100/Solid/blob/master/Solid/ParticleSwarm.py

    Parameters
    ----------
    G : object
        :class:`nx.Digraph()` must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

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

    swarm_size : int, optional
        number of members in swarm. Default : 50.

    member_size : int, optional
        number of components per member vector. Default : ``len(G.nodes())``.

    neighbourhood_size : int, optional
        size of neighbourhood. Default : 10.

    lower_bound : float, optional
        lower bound of initial positions. Default : -1.

    upper_bound : float, optional
        upper bound of initial positions. Default : 1.


    c1 : float, optional
        constant for 1st term in the velocity equation.
        Default : 1.35.

    c2 : float, optional
        contsant for 2nd term in the velocity equation.
        Default : 1.35.

    c3 : float, optional
        constant for 3rd term in the velocity equation.
        Default : 1.4.

    seed : None or int or numpy.random.RandomState instance, optional
        seed for PSOLGENT class. Default : None (which gives a single value
        numpy.random.RandomState).

    REF_callback : REFCallback, optional
        Custom resource extension callback. See `REFs`_ for more details.
        Default : None

    .. _REFs : https://cspy.readthedocs.io/en/latest/ref.html

    Raises
    ------
    Exception
        if no resource feasible path is found

    """

    __metaclass__ = ABCMeta

    def __init__(
        self,
        G: DiGraph,
        max_res: List[float],
        min_res: List[float],
        preprocess: Optional[bool] = False,
        max_iter: Optional[int] = 100,
        max_localiter: Optional[int] = 5,
        time_limit: Optional[int] = None,
        threshold: Optional[float] = None,
        swarm_size: Optional[int] = 50,
        member_size: Optional[int] = None,
        neighbourhood_size: Optional[int] = 10,
        lower_bound: Optional[float] = -1.0,
        upper_bound: Optional[float] = 1.0,
        c1: Optional[float] = 1.35,
        c2: Optional[float] = 1.35,
        c3: Optional[float] = 1.4,
        seed: RandomState = None,
        REF_callback: Callable = None,
    ):
        # Pass arguments to parent class
        super().__init__(G, max_res, min_res, preprocess, threshold, REF_callback)
        # Inputs
        self.max_iter = max_iter
        self.max_localiter = max_localiter
        self.time_limit = time_limit
        self.threshold = threshold
        self.swarm_size = swarm_size
        self.member_size = member_size or len(G.nodes())
        self.hood_size = neighbourhood_size
        self.lower_bound = lower_bound * np.ones(member_size)
        self.upper_bound = upper_bound * np.ones(member_size)
        self.c1 = float(c1)
        self.c2 = float(c2)
        self.c3 = float(c3)
        self.random_state = check_seed(seed)
        self.rands = np.ones(swarm_size)
        self.local_rands = np.ones(swarm_size)
        self.global_rands = np.ones(swarm_size)
        self.max_localiter = max_localiter
        # PSO Specific Parameters
        self.iter = 0
        self.pos = None
        self.vel = None
        self.best = None
        self.fitness = None
        self.best_fit = None
        self.local_best = None
        self.global_best = None
        self.sorted_nodes = self._sort_nodes(list(self.G.nodes()))
        self._best_path = None

    def _pos2path(self, pos, rands):
        new_disc = self._discretise_solution(pos, rands)
        return self._update_current_nodes(new_disc)

    def run(self):
        """Calculate shortest path with resource constraints."""
        start = time()
        self._init_swarm()
        while self.iter < self.max_iter and not check_time_limit_breached(
            start, self.time_limit
        ):
            pos_new = self.pos + self._get_vel()
            new_rands = self.random_state.uniform(0, 1, size=self.swarm_size)
            # Force Source and Sink to be selected
            pos_new[:, [0, -1]] = min(10 * self.lower_bound, np.min(pos_new))
            paths_new = np.empty(len(pos_new), dtype="object")
            paths_new[:] = [self._pos2path(p, r) for p, r in zip(pos_new, new_rands)]
            self._update_best(
                self.pos, pos_new, self.rands, new_rands, self.paths, paths_new
            )
            self.pos = pos_new
            self.rands = new_rands
            self.fitness = self._get_fitness(self.paths)
            self._global_best()
            # Save best results
            self.st_path = self._best_path
            self.check_feasibility()  # works on st_path
            # Update local best for each particle
            for i in range(self.swarm_size):
                self._local_best(i)
            if self.iter % 100 == 0:
                log.info(
                    "Iteration: {0}. Current best fit: {1}".format(
                        self.iter, self.best_fit
                    )
                )
            # Terminate if feasible path found with total cost <= threshold
            if (
                self.best_path
                and self.best_path_cost
                and self.threshold is not None
                and self.best_path_cost <= self.threshold
            ):
                break
            self.iter += 1
        if not self.best_path:
            raise Exception("No resource feasible path has been found")

    def _init_swarm(self):
        # Initialises the variables that are altered during the algorithm
        self.pos = self.random_state.uniform(
            self.lower_bound, self.upper_bound, size=(self.swarm_size, self.member_size)
        )
        self.rands = self.random_state.uniform(0, 1, size=self.swarm_size)
        self.vel = self.random_state.uniform(
            self.lower_bound - self.upper_bound,
            self.upper_bound - self.lower_bound,
            size=(self.swarm_size, self.member_size),
        )
        # Force Source and Sink to be selected
        self.pos[:, [0, -1]] = min(10 * self.lower_bound, np.min(self.pos))
        self.paths = np.empty(len(self.pos), dtype="object")
        self.paths[:] = [self._pos2path(p, r) for p, r in zip(self.pos, self.rands)]
        self.fitness = self._get_fitness(self.paths)
        self.best = np.copy(self.pos)
        self._global_best()
        self.local_best = np.copy(self.pos)

    def _get_vel(self):
        # Generate random numbers
        u1 = np.zeros((self.swarm_size, self.swarm_size))
        u1[np.diag_indices_from(u1)] = [
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size)
        ]

        u2 = np.zeros((self.swarm_size, self.swarm_size))
        u2[np.diag_indices_from(u2)] = [
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size)
        ]

        u3 = np.zeros((self.swarm_size, self.swarm_size))
        u3[np.diag_indices_from(u2)] = [
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size)
        ]

        # Coefficients
        c = self.c1 + self.c2 + self.c3
        chi_1 = 2 / abs(2 - c - sqrt(pow(c, 2) - 4 * c))
        # Returns velocity
        return (
            chi_1 * (self.vel + (self.c1 * np.dot(u1, (self.best - self.pos))))
            + (self.c2 * np.dot(u2, (self.global_best - self.pos)))
            + (self.c3 * np.dot(u3, (self.local_best - self.pos)))
        )

    # also implicitly updates self.best_path
    def _update_best(self, old, new, old_rands, new_rands, old_paths, new_paths):
        # Updates the best objective function values for each member
        old_fitness = np.array(self._get_fitness(old_paths))
        new_fitness = np.array(self._get_fitness(new_paths))
        best = np.zeros(shape=old.shape)  # * np.nan
        best_rands = np.zeros(shape=old_rands.shape)  # * np.nan
        best_paths = np.zeros(shape=len(old_paths), dtype="object")
        best_fitness = np.zeros(shape=len(old))
        if any(of < nf for of, nf in zip(old_fitness, new_fitness)):
            # replace indices in best with old members if lower fitness
            idx_old = [
                idx
                for idx, val in enumerate(zip(old_fitness, new_fitness))
                if val[0] < val[1]
            ]
            best[idx_old] = old[idx_old]
            best_rands[idx_old] = old_rands[idx_old]
            best_paths[idx_old] = old_paths[idx_old]
            best_fitness[idx_old] = old_fitness[idx_old]
            # replace this with just find the rows where it is all zero
            idx_new = np.all(best == 0, axis=1)
            # replace indices in best with new members if lower fitness
            best[idx_new] = new[idx_new]
            best_rands[idx_new] = new_rands[idx_new]
            best_paths[idx_new] = new_paths[idx_new]
            best_fitness[idx_new] = new_fitness[idx_new]
        else:
            best = new
            best_rands = new_rands
            best_paths = new_paths
            best_fitness = new_fitness
        self.best = np.array(best)
        self.best_rands = np.array(best_rands)
        self.best_paths = np.array(best_paths)
        self.best_fitness = np.array(best_fitness)
        # Update best known path if better
        if not self.best_fit or self.best_fit > min(self.best_fitness):
            self._best_path = list(self.best_paths[np.argmin(best_fitness)][:])

    def _global_best(self):
        # Updates the current global best across swarm
        if not self.best_fit or self.best_fit > min(self.fitness):
            self.global_best = np.array(
                [self.pos[np.argmin(self.fitness)]] * self.swarm_size
            )
            self.best_fit = min(self.fitness)  # update best fitness
            self.global_rand = self.rands[np.argmin(self.fitness)]
            self.global_path = self.paths[np.argmin(self.fitness)]
            self._best_path = list(self.global_path[:])

    def _local_best(self, i):
        """
        Updates the local best for particle i using a neighbourhood around it.
        """
        bottom = max(i - self.hood_size, 0)
        top = min(bottom + self.hood_size, len(self.fitness))
        if top - bottom < self.hood_size:
            # Maximum length reached
            bottom = top - self.hood_size
        _range = list(range(bottom, top + 1))
        min_idx = _range[np.argmin(self.fitness[bottom:top])]
        self.local_best[i] = self.pos[min_idx]
        self.local_rands[i] = self.rands[min_idx]

    # Fitness #
    # Fitness conversion to path representation of solutions and evaluation
    def _get_fitness(self, paths):
        # Applies objective function to all members of swarm
        return [self._evaluate_member(p) for p in paths]

    def _evaluate_member(self, path):
        return self._get_fitness_member(path)

    @staticmethod
    def _discretise_solution(member, rand):
        sig = np.array(1 / (1 + np.exp(-member)))
        return (sig < rand) * 1

    def _update_current_nodes(self, arr):
        """
        Saves binary representation of nodes in path.
        0 not present, 1 present.
        """
        nodes = self._sort_nodes(list(self.G.nodes()))
        current_nodes = [nodes[i] for i in range(len(nodes)) if arr[i] == 1]
        soln = Solution(current_nodes, np.inf)
        return self._local_search_2opt(soln).path

    def _get_fitness_member(self, path):
        # Returns the objective for a given path
        return self._fitness(path)

    def _fitness(self, nodes):
        edges = self._get_edges(nodes)
        disconnected, path = self._check_edges(edges)
        if edges:
            if disconnected:
                return 1e7  # disconnected path
            cost = self._check_path(path, edges)
            if cost is not False:
                # Valid path with penalty
                return cost
            else:
                return 1e6  # path not valid
        else:
            return 1e6  # no path

    # Path-related methods #
    def _get_edges(self, nodes):
        # Creates a list of edges given the nodes selected
        return [
            edge
            for edge in self.G.edges(self.G.nbunch_iter(nodes), data=True)
            if edge[0:2] in zip(nodes, nodes[1:])
        ]

    @staticmethod
    def _check_edges(edges):
        """
        If edges given, saves the path provided.
        Returns whether the path is disconnected or not
        """
        if edges:
            path = [edge[0] for edge in edges]
            path.append(edges[-1][1])
            return any(edge[1] not in path for edge in edges), path
        else:
            return None, None

    def _check_path(self, path, edges):
        """
        Returns False if path is not valid
        Penalty/cost otherwise
        """
        if not path:
            return False
        if len(path) >= 2 and (path[0] == "Source" and path[-1] == "Sink"):
            base_cost = sum(edge[2]["weight"] for edge in edges)
            # save st_path to reload later
            old_path = self.st_path
            self.st_path = path[:]
            if self.check_feasibility(save=True) is True:
                log.debug("Resource feasible path found")
                self.st_path = old_path
                return base_cost
            else:
                # penalty for resource infeasible valid path
                self.st_path = old_path
                return 1e5 + base_cost
        else:
            return False

    @staticmethod
    def _sort_nodes(nodes):
        """
        Sort nodes between Source and Sink. If node data allows sorting,
        edit the line below to pass `list(self.G.nodes(data=True))` and use that
        in the sorting function below.

        For example, if nodes have an attribute `pos` a tuple that contains
        the position of a node in space (x, y), replace the return with:
        `return sorted(nodes, key=lambda n: n[1]['pos'][0])`
        edit the sorting function to make use of it.
        """
        return (
            ["Source"]
            + sorted([n for n in nodes if n not in ["Source", "Sink"]])
            + ["Sink"]
        )

    def _local_search_2opt(self, solution):
        """
        2-opt heuristic.
        In this implementation the number of iterations is by the the minimum
        between `max_localiter` and the number of iterations that would
        correspond for 2opt (try swapping every feasible pair in a path).

        See https://en.wikipedia.org/wiki/2-opt
        """

        def _2opt_swap(path, i, j):
            """
            2-opt swap only if resulting path is connected in the original
            graph.
            """
            if (
                (path[: i + 1][-1], path[j:i:-1][0]) in self.G.edges()
                and (
                    (
                        len(path[j:i:-1]) > 0
                        and all(
                            _ in self.G.edges()
                            for _ in zip(path[j:i:-1], path[j:i:-1][1:])
                        )
                    )
                    or len(path[j:i:-1]) == 0
                )
                and (path[j:i:-1][-1], path[j + 1 :][0]) in self.G.edges()
            ):
                return path[: i + 1] + path[j:i:-1] + path[j + 1 :]
            return None

        local_iter = 0
        path_length = len(solution.path)  # just in case
        # Run 2opt but stop earlier if iterations exceed max_localiter
        # Range of swappable nodes exclude source and sink
        for i in range(0, path_length - 1):  # Local search phase
            # Init candidate solution using random valid path generator
            for j in range(i + 1, path_length - 1):
                candidate = Solution(_2opt_swap(solution.path, i, j), 0)
                # evaluate candidate solution
                if candidate.path is not None:
                    candidate.cost = self._fitness(candidate.path)
                    # Update solution with candidate if lower cost and resource feasible
                    # TODO: difference if we break at first improvement
                    if (
                        candidate.cost or candidate.cost == 0
                    ) and candidate.cost < solution.cost:
                        solution = candidate
                        # break
                if local_iter == self.max_localiter:
                    break
                local_iter += 1
        return solution
