"""
Adapted from https://github.com/100/Solid/blob/master/Solid/ParticleSwarm.py
"""

from __future__ import absolute_import
from __future__ import print_function

from math import sqrt
from abc import ABCMeta
from operator import add
from logging import getLogger
from numpy.random import RandomState
from numpy import (argmin, array, copy, diag_indices_from, exp, dot, zeros,
                   ones, where)

# Local imports
from cspy.checking import check
from cspy.algorithms.path import Path
from cspy.preprocessing import preprocess_graph

log = getLogger(__name__)


class StandardGraph:
    def __init__(self, G, max_res, min_res, REF, preprocess):
        # Check inputs
        check(G, max_res, min_res, REF)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF)
        self.max_res = max_res
        self.min_res = min_res
        self.path_list = None
        self.best_path = None
        self.path_edges = None
        # Set path class attribute
        if REF:
            Path._REF = REF
        else:
            Path._REF = add

    def _get_path_edges(self, nodes):
        # Creates a list of edges given the nodes selected
        self.path_edges = list(
            edge for edge in self.G.edges(self.G.nbunch_iter(nodes), data=True)
            if edge[0:2] in zip(nodes, nodes[1:]))

    def _save_shortest_path(self):
        """
        If edges given, saves the path provided.
        Returns whether the path is disconnected or not
        """
        if self.path_edges:
            self.path_list = [edge[0] for edge in self.path_edges]
            self.path_list.append(self.path_edges[-1][1])
            return any(edge[1] not in self.path_list
                       for edge in self.path_edges)

    def _check_path(self):
        """
        Returns False if path is not valid
        Penalty otherwise
        """
        if self.path_list:
            if len(self.path_list) > 2 and (self.path_list[0] == 'Source'
                                            and self.path_list[-1] == 'Sink'):
                base_cost = sum(edge[2]['weight'] for edge in self.path_edges)
                # if self.path[0] == 'Source' and self.path[-1] == 'Sink':
                path = Path(self.G, self.path_list, self.max_res, self.min_res)
                if path.check_feasibility() is True:
                    self.best_path = path
                    log.debug("Resource feasible path found")
                    return base_cost
                else:
                    # penalty for resource infeasible valid path
                    return 1e5 + base_cost
            else:
                return False
        else:
            return False


class PSOLGENT(StandardGraph):
    """
    Particle Swarm Optimization with combined Local and Global Expanding
    Neighborhood Topology (PSOLGENT) algorithm for the (resource)
    constrained shortest path problem (`Marinakis et al 2017`_).


    Given the nature of our problem we have set the default parameters of
    the algorithm as suggested in the paper mentioned.

    Code adapted from `Solid`_.

    .. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302357z

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

    REF : function, optional
        Custom resource extension function. See `REFs`_ for more details.
        Default : additive.

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    max_iter : int, optional
        Maximum number of iterations for algorithm. Default : 100.

    swarm_size : int, optional
        number of members in swarm. Default : 50.

    member_size : int, optional
        number of components per member vector. Default : ``len(G.nodes())``.

    neighbourhood_size : int, optional
        size of neighbourhood. Default : 10.

    lower_bound : list of floats, optional
        list of lower bounds. Default : ``numpy.zeros(member_size)``
        (no nodes in path).

    upper_bound : list of floats, optional
        list of upper bounds. Default : ``numpy.ones(member_size)``
        (all nodes in path).

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

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs

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
    See `Using cspy`_.

    This algorithm requires a consistent sorting of the nodes in the graph.
    Please see comments and edit the function ``_sort_nodes`` accordingly.

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

    Example
    -------
    To run the algorithm, create a :class:`PSOLGENT` instance and call `run`.

    .. code-block:: python

        >>> from cspy import PSOLGENT
        >>> from networkx import DiGraph
        >>> from numpy import zeros, ones, array
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('Source', 'B', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('Source', 'C', res_cost=array([10, 1]), weight=10)
        >>> G.add_edge('A', 'C', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('A', 'E', res_cost=array([10, 1]), weight=10)
        >>> G.add_edge('A', 'F', res_cost=array([10, 1]), weight=10)
        >>> G.add_edge('B', 'C', res_cost=array([2, 1]), weight=-1)
        >>> G.add_edge('B', 'F', res_cost=array([10, 1]), weight=10)
        >>> G.add_edge('B', 'E', res_cost=array([10, 1]), weight=10)
        >>> G.add_edge('C', 'D', res_cost=array([1, 1]), weight=-1)
        >>> G.add_edge('D', 'E', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('D', 'F', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('D', 'Sink', res_cost=array([10, 10]), weight=10)
        >>> G.add_edge('F', 'Sink', res_cost=array([10, 1]), weight=1)
        >>> G.add_edge('E', 'Sink', res_cost=array([1, 1]), weight=1)
        >>> n_nodes = len(G.nodes())
        >>> psolgent = PSOLGENT(G, [5, 5], [0, 0],
                                max_iter=200,
                                swarm_size=50,
                                member_size=n_nodes,
                                neighbourhood_size=50)
        >>> psolgent.run()
        >>> print(psolgent.path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']

    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 REF=None,
                 preprocess=False,
                 max_iter=100,
                 swarm_size=50,
                 member_size=None,
                 lower_bound=None,
                 upper_bound=None,
                 neighbourhood_size=10,
                 c1=1.35,
                 c2=1.35,
                 c3=1.4,
                 seed=None):
        # Init graph
        StandardGraph.__init__(self, G, max_res, min_res, REF, preprocess)
        # Inputs
        self.swarm_size = swarm_size
        self.member_size = member_size if member_size else len(G.nodes())
        self.hood_size = neighbourhood_size
        self.lower_bound = zeros(member_size)
        self.upper_bound = ones(member_size)
        self.c1 = float(c1)
        self.c2 = float(c2)
        self.c3 = float(c3)
        self.max_iter = max_iter
        # PSO Specific Parameters
        self.iter = 0
        self.pos = None
        self.vel = None
        self.best = None
        self.fitness = None
        self.best_fit = None
        self.local_best = None
        self.global_best = None
        # Check seed and init `random_state`. Altered from:
        # https://github.com/scikit-learn/scikit-learn/blob/92af3dabbb5f3381a656f7727171f332b8928e05/sklearn/utils/validation.py#L764-L782
        if seed is None:
            self.random_state = RandomState()
        elif isinstance(seed, int):
            self.random_state = RandomState(seed)
        elif isinstance(seed, RandomState):
            self.random_state = seed
        else:
            raise Exception("{} cannot be used to seed".format(seed))

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        self._init_swarm()
        while self.iter < self.max_iter:
            pos_new = self.pos + self._get_vel()
            self._update_best(self.pos, pos_new)
            self.pos = pos_new
            self.fitness = self._get_fitness(self.pos)
            self._global_best()
            self._local_best(self.iter, self.hood_size)
            if self.iter % 100 == 0:
                log.info("Iteration: {0}. Current best fit: {1}".format(
                    self.iter, self.best_fit))
            self.iter += 1
        if self.best_path:
            pass
        else:
            raise Exception("No resource feasible path has been found")

    @property
    def path(self):
        """
        Get list with nodes in calculated path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path.path

    @property
    def total_cost(self):
        """
        Get accumulated cost along the path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path.cost

    @property
    def consumed_resources(self):
        """
        Get accumulated resources consumed along the path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path.total_res

    def _init_swarm(self):
        # Initialises the variables that are altered during the algorithm
        self.pos = self.random_state.uniform(self.lower_bound,
                                             self.upper_bound,
                                             size=(self.swarm_size,
                                                   self.member_size))
        self.vel = self.random_state.uniform(
            self.lower_bound - self.upper_bound,
            self.upper_bound - self.lower_bound,
            size=(self.swarm_size, self.member_size))
        self.fitness = self._get_fitness(self.pos)
        self.best = copy(self.pos)
        self._global_best()
        self.local_best = copy(self.pos)

    def _get_vel(self):
        # Generate random numbers
        u1 = zeros((self.swarm_size, self.swarm_size))
        u1[diag_indices_from(u1)] = list(
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size))
        u2 = zeros((self.swarm_size, self.swarm_size))
        u2[diag_indices_from(u2)] = list(
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size))
        u3 = zeros((self.swarm_size, self.swarm_size))
        u3[diag_indices_from(u2)] = list(
            self.random_state.uniform(0, 1) for _ in range(self.swarm_size))
        # Coefficients
        c = self.c1 + self.c2 + self.c3
        chi_1 = 2 / abs(2 - c - sqrt(pow(c, 2) - 4 * c))
        # Returns velocity
        return (chi_1 * (self.vel + (self.c1 * dot(u1,
                                                   (self.best - self.pos)))) +
                (self.c2 * dot(u2, (self.global_best - self.pos))) +
                (self.c3 * dot(u3, (self.local_best - self.pos))))

    def _update_best(self, old, new):
        # Updates the best objective function values for each member
        old_fitness = array(self._get_fitness(old))
        new_fitness = array(self._get_fitness(new))
        best = zeros(shape=old.shape)
        if any(of < nf for of, nf in zip(old_fitness, new_fitness)):
            # replace indices in best with old members if lower fitness
            idx_old = list(
                idx for idx, val in enumerate(zip(old_fitness, new_fitness))
                if val[0] < val[1])
            best[idx_old] = old[idx_old]
            idx_new = where(best == 0)
            # replace indices in best with new members if lower fitness
            best[idx_new] = new[idx_new]
        else:
            best = new
        self.best = array(best)

    def _global_best(self):
        # Updates the global best across swarm
        if not self.best_fit or self.best_fit > min(self.fitness):
            self.global_best = array([self.pos[argmin(self.fitness)]] *
                                     self.swarm_size)
            self.best_fit = min(self.fitness)  # update best fitness

    def _local_best(self, i, hood_size):
        # Updates the local best across swarm
        bottom = max(i - hood_size, 0)
        top = min(bottom + hood_size, len(self.fitness))
        if top - bottom < hood_size:
            # Maximum length reached
            bottom = top - hood_size
        self.local_best = array([self.pos[argmin(self.fitness[bottom:top])]] *
                                self.swarm_size)

    ###########
    # Fitness #
    ###########
    # Fitness conversion to path representation of solutions and evaluation
    def _get_fitness(self, pos):
        # Applies objective function to all members of swarm
        return list(map(self._evaluate_member, pos))

    def _evaluate_member(self, member):
        rand = self.random_state.uniform(0, 1)
        self._update_current_nodes(self._discretise_solution(member, rand))
        return self._get_fitness_member()

    @staticmethod
    def _discretise_solution(member, rand):
        sig = array(1 / (1 + exp(-member)))
        return array([1 if s < rand else 0 for s in sig])

    def _update_current_nodes(self, arr):
        """ Saves binary representation of nodes in path.
        0 not present, 1 present. """
        nodes = self._sort_nodes(list(self.G.nodes()))
        self.current_nodes = list(nodes[i] for i in range(len(nodes))
                                  if arr[i] == 1)

    def _get_fitness_member(self):
        # Returns the objective for a given path
        self._get_path_edges(self.current_nodes)
        disconnected = self._save_shortest_path()
        if self.path_edges:
            if disconnected:
                return 1e7  # disconnected path
            cost = self._check_path()
            if cost is not False:
                # Valid path with penalty
                return cost
            else:
                return 1e6  # path not valid
        else:
            return 1e6  # no path

    @staticmethod
    def _sort_nodes(nodes):
        """ Sort nodes between Source and Sink. If node data allows sorting,
        edit line 327 to pass `list(self.G.nodes(data=True))` and used that
        in the sorting function below.
        For example, if nodes have an attribute `pos` a tuple that contains
        the position of a node in space (x, y), replace the return with:
        `return sorted(nodes, key=lambda n: n[1]['pos'][0])`
        edit the sorting function to make use of it.
        """
        order_dict = {'Source': '0', 'Sink': 'Z{}'.format(len(nodes))}
        return sorted(nodes,
                      key=lambda x: order_dict[x] if x in order_dict else x)
