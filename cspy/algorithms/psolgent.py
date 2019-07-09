"""
Adapted from https://github.com/100/Solid/blob/master/Solid/ParticleSwarm.py
"""

from __future__ import absolute_import
from __future__ import print_function

import logging
from abc import ABCMeta
from math import sqrt
from random import random
from numpy import (apply_along_axis, argmin, array, copy, diag_indices_from,
                   exp, dot, zeros, ones)
from numpy.random import uniform
from cspy.path import Path
from cspy.preprocessing import check

log = logging.getLogger(__name__)


class StandardGraph:

    def __init__(self, G, max_res, min_res):
        # Check input graph and parameters
        check(G, max_res, min_res)
        # Input parameters
        self.G = G
        self.max_res = max_res
        self.min_res = min_res
        self.best_path = None

    def _check_path(self, path):
        """
        Returns False if input path is not valid
        Penalty otherwise
        """
        if path:
            if (len(path) > 2 and path[0] == 'Source' and path[-1] == 'Sink'):
                if Path(self.G, path, self.max_res,
                        self.min_res)._check_feasibility() is True:
                    self.best_path = path
                    return 0
                else:
                    return 1e2
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

    Code adapted from `Solid`_

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

    max_iter : int
        Maximum number of iterations for algorithm

    swarm_size : int
        number of members in swarm

    member_size : int
        number of components per member vector

    neighbourhood_size : int
        size of neighbourhood

    lower_bound : list of floats, optional
        list of lower bounds

    upper_bound : list of floats, optional
        list of upper bounds

    c1 : float, optional
        constant for 1st term in the velocity equation

    c2 : float, optional
        contsant for 2nd term in the velocity equation

    c3 : float, optional
        constant for 3rd term in the velocity equation

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

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

    Example
    -------
    To run the algorithm, create a :class:`PSOLGENT` instance and call `run`.

    .. code-block:: python

        >>> from cspy import PSOLGENT
        >>> from networkx import DiGraph
        >>> from numpy import zeros, ones
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
        >>> n_nodes = len(self.J.nodes())
        >>> path = PSOLGENT(G, [5, 5], [0, 0], 100, 50, n_nodes, 50,
                        zeros(n_nodes), ones(n_nodes), 1.35, 1.5, 1.40).run()
        >>> print(path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']


    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 max_iter,
                 swarm_size,
                 member_size,
                 neighbourhood_size,
                 c1=1.35,
                 c2=1.35,
                 c3=1.40):
        # Init graph
        StandardGraph.__init__(self, G, max_res, min_res)
        # Inputs
        self.swarm_size = swarm_size
        self.member_size = member_size
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
        self.curr_obj = None
        self.local_best = None
        self.global_best = None
        self.shortest_path = None

    def run(self):
        self._init_swarm()
        while self.iter < self.max_iter:
            vel_new = self._get_vel_new()
            pos_new = self.pos + vel_new

            self._best(self.pos, pos_new)
            self.pos = pos_new
            self.scores = self._score(self.pos)
            self._global_best()
            self._local_best(self.iter)
            self.iter += 1
        if self.best_path:
            return self.best_path
        else:
            raise Exception("No resource feasible path has been found")

    def _init_swarm(self):
        # Initialises the variables that are altered during the algorithm
        self.pos = uniform(self.lower_bound,
                           self.upper_bound,
                           size=(self.swarm_size, self.member_size))
        self.vel = uniform(self.lower_bound - self.upper_bound,
                           self.upper_bound - self.lower_bound,
                           size=(self.swarm_size, self.member_size))
        self.scores = self._score(self.pos)
        self.best = copy(self.pos)
        self._global_best()
        self.local_best = copy(self.pos)

    def _get_vel_new(self):
        # Generate random numbers
        u1 = zeros((self.swarm_size, self.swarm_size))
        u1[diag_indices_from(u1)] = [random() for _ in range(self.swarm_size)]
        u2 = zeros((self.swarm_size, self.swarm_size))
        u2[diag_indices_from(u2)] = [random() for _ in range(self.swarm_size)]
        u3 = zeros((self.swarm_size, self.swarm_size))
        u3[diag_indices_from(u3)] = [random() for _ in range(self.swarm_size)]
        # Coefficients
        c = self.c1 + self.c2 + self.c3
        chi_1 = 2 / abs(2 - c - sqrt(pow(c, 2) - 4 * c))
        # Returns velocity
        return (chi_1 * (self.vel + (self.c1 * dot(u1,
                                                   (self.best - self.pos)))) +
                (self.c2 * dot(u2, (self.global_best - self.pos))) +
                (self.c3 * dot(u3, (self.local_best - self.pos))))

    def _best(self, old, new):
        # Updates the best objective function values for each member
        old_scores = self._score(old)
        new_scores = self._score(new)
        best = []
        for i in range(len(old_scores)):
            if old_scores[i] < new_scores[i]:
                best.append(old[i])
            else:
                best.append(new[i])
        self.best = array(best)

    def _global_best(self):
        # Finds the global best across swarm
        if self.global_best is None:
            self.global_best = array([self.pos[argmin(self.scores)]] *
                                     self.swarm_size)
            self.curr_obj = min(self.scores)

    def _local_best(self, i):
        bottom = max(i - self.hood_size, 0)
        top = min(bottom + self.hood_size, len(self.scores))
        if top - bottom < self.hood_size:
            # Maximum length reached
            bottom = top - self.hood_size
        self.local_best = array([self.pos[argmin(self.scores[bottom:top])]] *
                                self.swarm_size)

    ###########
    # Fitness #
    ###########
    # Fitness conversion to path representation of solutions and evaluation
    def _score(self, pos):
        # Applies objective function to all members of swarm
        return apply_along_axis(self._objective, 1, pos)

    def _objective(self, member):
        rand = random()
        self._update_current_nodes(self._discretise_solution(member, rand))
        return self._get_objective()

    def _discretise_solution(self, member, rand):
        self.sig = array(1 / (1 + exp(-member)))
        return array([1 if s < rand else 0 for s in self.sig])

    def _update_current_nodes(self, arr):
        """ Saves binary representation of nodes in path.
        0 not present 1 present. """
        nodes = self._sort_nodes(list(self.G.nodes()))
        self.current_nodes = list(
            nodes[i] for i in range(len(nodes)) if arr[i] == 1)

    def _get_path_edges(self):
        # Creates a list of edges given the nodes selected
        shortest_path_edges = list(
            edge for edge in self.G.edges(
                self.G.nbunch_iter(self.current_nodes), data=True)
            if edge[0:2] in zip(self.current_nodes, self.current_nodes[1:]))
        return shortest_path_edges

    def _save_shortest_path(self, shortest_path_edges):
        """If edges given, saves the path provided.
        Returns whether the path is disconnected or not"""
        if shortest_path_edges:
            self.shortest_path = [edge[0] for edge in shortest_path_edges]
            self.shortest_path.append(shortest_path_edges[-1][1])
            return any(edge[1] not in self.shortest_path
                       for edge in shortest_path_edges)

    def _get_objective(self):
        # Returns the objective for a given path
        shortest_path_edges = self._get_path_edges()
        disconnected = self._save_shortest_path(shortest_path_edges)
        if shortest_path_edges:
            if disconnected:
                return 1e5  # disconnected path
            penalty = self._check_path(self.shortest_path)
            if penalty is not False:
                # Valid path with penalty
                return penalty + sum(
                    edge[2]['weight'] for edge in shortest_path_edges)
            else:
                return 1e5  # path not valid
        else:
            return 1e10  # no path

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])

    @staticmethod
    def _sort_nodes(nodes):
        # Sort nodes between Source and Sink
        order_dict = {'Source': '0', 'Sink': 'Z{}'.format(len(nodes))}
        # String comparison for all nodes keeping source first and sink last
        return sorted(nodes,
                      key=lambda x: order_dict[x] if x in order_dict else x)
