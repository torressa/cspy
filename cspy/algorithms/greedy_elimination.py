from __future__ import absolute_import
from __future__ import print_function

import logging
from numpy import array
from networkx import astar_path, NetworkXException

# Local imports
from cspy.checking import check
from cspy.algorithms.path import Path
from cspy.preprocessing import preprocess_graph

log = logging.getLogger(__name__)


class GreedyElim:
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

    return_G : bool, optional
        whether or not you'd like the resulting graph returned

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
                 return_G=False):
        # Check inputs
        check(G, max_res, min_res, REF)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF)
        # Input parameters
        self.max_res = max_res
        self.min_res = min_res
        # Algorithm specific parameters
        self.it = 0
        self.stop = False
        self.predecessor_edges = []
        self.last_edge_removed = None
        self.edges_to_remove = dict(self.G.edges())
        # To return
        self.best_path = []

        if REF:
            Path._REF = REF

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        while self.stop is False:
            self._algorithm()
            self.it += 1

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
            path = astar_path(self.G, 'Source', 'Sink')
        except NetworkXException:
            pass
        if path:
            _path = Path(self.G, path, self.max_res, self.min_res)
            edge_or_true = _path.check_feasibility()
            if edge_or_true is True:
                self.best_path = _path
                self.stop = True
            else:
                self._update_graph(edge_or_true)
        else:
            self.G.add_edge(*self.last_edge_removed[:2],
                            res_cost=self.last_edge_removed[2]['res_cost'],
                            weight=self.last_edge_removed[2]['weight'])
            self._update_graph(
                self._get_predecessor_edges(self.last_edge_removed))

    def _update_graph(self, edge=None):
        self.G.remove_edge(*edge[:2])
        self.last_edge_removed = edge

    def _get_predecessor_edges(self, edge):
        if not self.predecessor_edges:
            node = edge[0]
            if node == "Source":
                self.stop = True
                return edge
            self.predecessor_edges = [
                e for e in self.G.edges(self.G.nbunch_iter(
                    [node] + list(self.G.predecessors(node))),
                                        data=True)
                if e[1] == node and e != edge
            ]
            self.predecessor_edges.sort(key=lambda x: x[2]['weight'])
        next_edge = self.predecessor_edges[-1]
        self.predecessor_edges.pop(-1)
        return next_edge

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])
