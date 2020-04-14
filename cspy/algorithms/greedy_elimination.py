from __future__ import absolute_import
from __future__ import print_function

import logging
from numpy import array
from networkx import NetworkXException

# Local imports
from cspy.algorithms.path_base import PathBase

log = logging.getLogger(__name__)


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

    Returns
    -------
    path : list
        nodes in shortest path obtained.

    Raises
    ------
    Exception
        if no resource feasible path is found

    Notes
    -----
    The input graph must have a ``n_res`` attribute.
    The edges in the graph must all have a ``res_cost`` attribute.
    See `Using cspy`_

    .. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html


    Example
    -------
    To run the algorithm, create a :class:`GreedyElim` instance and call `run`.

    .. code-block:: python

        >>> from cspy import GreedyElim
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
        >>> greedelim = GreedyElim(G, max_res, min_res)
        >>> greedelim.run()
        >>> print(greedelim.path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']

    """

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 REF=None,
                 preprocess=False,
                 max_depth=1000):
        # Pass arguments to parent class
        super().__init__(G, max_res, min_res, REF, preprocess)
        # Algorithm specific parameters
        self.max_depth = max_depth
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
        while self.stop is False:
            self._algorithm()

        if self.best_path:
            pass
        else:
            raise Exception("No resource feasible path has been found")

    def _algorithm(self):
        path = []
        try:
            path = self.update_simple_path("Source", self.max_depth)
        except NetworkXException:
            pass
        if path:
            self.st_path = path
            edge_or_true = self.check_feasibility()
            if edge_or_true is True:
                self.stop = True
            else:
                self.remove_edge(edge_or_true)
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
