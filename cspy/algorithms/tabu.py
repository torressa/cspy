from __future__ import absolute_import
from __future__ import print_function

from logging import getLogger
from collections import deque
from networkx import NetworkXException

# Local imports
from cspy.algorithms.path_base import PathBase

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

    REF : function, optional
        Custom resource extension function. See `REFs`_ for more details.
        Default : additive.

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    max_depth : int, optional
        depth for search of shortest simple path. Default : 1000.
        If the total number of simple paths is less than max_depth,
        then the shortest path is used.

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs


    Notes
    -----
    The input graph must have a ``n_res`` attribute.
    The edges in the graph must all have a ``res_cost`` attribute.
    See `Using cspy`_

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

    Example
    -------
    To run the algorithm, create a :class:`Tabu` instance, call `run`, and then
    query the attributes of interest: `path`, `total_cost`, or
    `consumed_resources`.

    .. code-block:: python

        >>> from cspy import Tabu
        >>> from networkx import DiGraph
        >>> from numpy import array
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('Source', 'B', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('A', 'C', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('B', 'C', res_cost=array([2, 1]), weight=-1)
        >>> G.add_edge('C', 'D', res_cost=array([1, 1]), weight=-1)
        >>> G.add_edge('D', 'E', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('D', 'F', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('F', 'Sink', res_cost=array([1, 1]), weight=1)
        >>> G.add_edge('E', 'Sink', res_cost=array([1, 1]), weight=1)
        >>> max_res, min_res = [5, 5], [0, 0]
        >>> tabu = Tabu(G, max_res, min_res)
        >>> tabu.run()
        >>> print(tabu.path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']

    """

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 REF=None,
                 preprocess=False,
                 max_depth=1000):
        # Pass arguments to SimplePath object
        super().__init__(G, max_res, min_res, REF, preprocess)
        # Algorithm specific parameters
        self.max_depth = max_depth
        self.iteration = 0
        self.stop = False
        self.neighbour = 'Source'
        self.neighbourhood = list()
        self.tabu_edge = None
        self.edges_to_check = dict(self.G.edges())

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        while self.stop is False:
            self._algorithm()
            self.iteration += 1

        if self.best_path:
            pass
        else:
            raise Exception("No resource feasible path has been found")

    def _algorithm(self):
        path = []
        try:
            path = self.update_simple_path(self.neighbour, self.max_depth)
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
            self.st_path = list(node for node in self.st_path if
                                (node != neighbour and self.st_path.index(node)
                                 < self.st_path.index(neighbour))) + path
        else:
            self._merge_paths(neighbour, path)

    def _merge_paths(self, neighbour, path):
        branch_path = [n for n in self.st_path if n not in path]
        for node in reversed(branch_path):
            if (node, neighbour) in self.G.edges():
                self.st_path = list(n for n in branch_path if (
                    branch_path.index(n) <= branch_path.index(node))) + path
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
