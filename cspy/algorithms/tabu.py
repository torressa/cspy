from __future__ import absolute_import
from __future__ import print_function

from operator import add
from networkx import astar_path, NetworkXException

# Local imports
from cspy.checking import check
from cspy.algorithms.path import Path
from cspy.preprocessing import preprocess_graph


class Tabu:
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

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs

    Returns
    -------
    path : list
        nodes in shortest path obtained.

    Notes
    -----
    The input graph must have a ``n_res`` attribute.
    The edges in the graph must all have a ``res_cost`` attribute.
    See `Using cspy`_

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

    Example
    -------
    To run the algorithm, create a :class:`Tabu` instance and call `run`.

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
    def __init__(self, G, max_res, min_res, REF=None, preprocess=False):
        # Check inputs
        check(G, max_res, min_res, REF)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF)
        # Input parameters
        self.max_res = max_res
        self.min_res = min_res
        # Algorithm specific parameters
        self.iteration = 0
        self.current_path = list()
        self.best_path = list()
        self.stop = False
        self.neighbour = 'Source'
        self.neighbourhood = list()
        self.tabu_edge = None
        self.edges_to_check = dict(self.G.edges())
        # To return
        self.best_path = None
        # Set path class attribute
        if REF:
            Path._REF = REF
        else:
            Path._REF = add

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

    def _algorithm(self):
        path = []
        try:
            path = astar_path(self.G,
                              self.neighbour,
                              'Sink',
                              heuristic=self._heuristic)
        except NetworkXException:
            pass
        if path:
            self._update_path(path)
            # Create path object
            _path = Path(self.G, self.current_path, self.max_res, self.min_res)
            edge_or_true = _path.check_feasibility()
            if edge_or_true is True:
                self.stop = True
                self.best_path = _path
            else:
                self._get_neighbour(edge_or_true)
        else:
            self._get_neighbour(self.tabu_edge)

    def _update_path(self, path):
        # Joins path using previous path and [neighbour, ..., sink] path
        if self.iteration == 0:
            self.current_path = path
        if self.neighbour in self.current_path:
            # Update current_path attribute
            self.current_path = list(node for node in self.current_path if (
                node != self.neighbour and self.current_path.index(
                    node) < self.current_path.index(self.neighbour))) + path
        else:
            self._merge_paths(path)

    def _merge_paths(self, path):
        branch_path = [n for n in self.current_path if n not in path]
        for node in reversed(branch_path):
            if (node, self.neighbour) in self.G.edges():
                self.current_path = list(n for n in branch_path if (
                    branch_path.index(n) <= branch_path.index(node))) + path
                break

    def _get_neighbour(self, edge=None):
        if self.edges_to_check:
            if edge and edge[:2] in self.edges_to_check:
                # If edge not already been seen
                current_edge = edge
            elif edge[0] == "Source":
                self.stop = True
                return
            else:
                current_edge = self._get_next_neighbour_edge(self.tabu_edge)
        else:
            self.stop = True
            return
        self.edges_to_check.pop(current_edge[:2], None)
        self.neighbour = current_edge[0]
        self.tabu_edge = current_edge

    def _get_next_neighbour_edge(self, edge):
        # Retrieves the edge adjacent to node with the least weight
        if not self.neighbourhood:
            node = edge[0]
            if node == "Source":
                self.stop = True
                return edge
            self.neighbourhood = list(e for e in self.G.edges(
                self.G.nbunch_iter([node] + list(self.G.predecessors(node))),
                data=True) if e[1] == node and e != edge)
            self.neighbourhood.sort(key=lambda x: x[2]['weight'])
        next_edge = self.neighbourhood[-1]
        self.neighbourhood.pop(-1)
        return next_edge

    def _heuristic(self, i, j):
        # Given a node pair returns a weight to apply
        if (i, j) == self.tabu_edge:
            return 1e7
        else:
            return 0
