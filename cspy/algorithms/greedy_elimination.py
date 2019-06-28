from __future__ import absolute_import
from __future__ import print_function

import logging
import numpy as np
from networkx import astar_path, NetworkXException
from cspy.label import Label
from cspy.preprocessing import check


class GreedyElim:
    """
    Simple heuristic algorithm for the (resource) constrained shortest
    path problem.

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

     max_res : list of floats
        :math:`[L, M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    min_res : list of floats
        :math:`[U, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    Returns
    -------
    path : list
        nodes in shortest path obtained.

    Notes
    -----
    The input graph must have a ``n_res`` attribute in the input graph has
    to be :math:`\geq 2`. The edges in the graph must all have a `res_cost`
    attribute.

    Example
    -------
    To run the algorithm, create a :class:`GreedyElim` instance and call `run`.

    .. code-block:: python

        >>> from cspy import GreedyElim
        >>> G = nx.DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=[1, 1], weight=1)
        >>> G.add_edge('Source', 'B', res_cost=[1, 1], weight=1)
        >>> G.add_edge('A', 'C', res_cost=[1, 1], weight=1)
        >>> G.add_edge('B', 'C', res_cost=[2, 1], weight=-1)
        >>> G.add_edge('C', 'D', res_cost=[1, 1], weight=-1)
        >>> G.add_edge('D', 'E', res_cost=[1, 1], weight=1)
        >>> G.add_edge('D', 'F', res_cost=[1, 1], weight=1)
        >>> G.add_edge('F', 'Sink', res_cost=[1, 1], weight=1)
        >>> G.add_edge('E', 'Sink', res_cost=[1, 1], weight=1)
        >>> max_res, min_res = [5, 5], [0, 0]
        >>> path = GreedyElim(G, max_res, min_res).run()
        >>> print(path)
        ['Source', 'A', 'C', 'D', 'E', 'Sink']

    """

    def __init__(self, G, max_res, min_res):
        # Check input graph and parameters
        check(G, max_res, min_res)
        # Input parameters
        self.G = G
        self.max_res = max_res
        self.min_res = min_res
        # Algorithm specific parameters
        self.it = 0
        self.path = []
        self.stop = False
        self.predecessor_edges = []
        self.last_edge_removed = None
        self.edges_to_remove = dict(self.G.edges())
        # Import function from cspy.label.Label
        self.check_feasibility = Label.check_geq

    def run(self):
        while self.stop is False:
            self.algorithm()
            self.it += 1

        if self.path:
            logging.debug(self.path)
            return self.path
        else:
            raise Exception("No resource feasible path has been found")

    def algorithm(self):
        path = []
        try:
            path = astar_path(self.G, 'Source', 'Sink')
        except NetworkXException:
            pass
        if path:
            shortest_path_edges = (
                edge for edge in self.G.edges(
                    self.G.nbunch_iter(path), data=True)
                if edge[0:2] in zip(path, path[1:]))
            total_res = np.zeros(self.G.graph['n_res'])
            # Check path for resource feasibility by adding one edge at a time
            for edge in shortest_path_edges:
                total_res += self._edge_extract(edge)
                if (self.check_feasibility(self.max_res, total_res) and
                        self.check_feasibility(total_res, self.min_res)):
                    pass
                else:
                    self._update_graph(edge)
                    break
            else:  # no break so resource feasible path found
                self.path = path
                self.stop = True
        else:
            self.G.add_edge(*self.last_edge_removed[:2],
                            res_cost=self.last_edge_removed[2]['res_cost'],
                            weight=self.last_edge_removed[2]['weight'])
            self._update_graph(
                self.get_predecessor_edges(self.last_edge_removed))

    def _update_graph(self, edge=None):
        self.G.remove_edge(*edge[: 2])
        self.last_edge_removed = edge

    def get_predecessor_edges(self, edge):
        if not self.predecessor_edges:
            node = edge[0]
            if node == "Source":
                self.stop = True
                return edge
            self.predecessor_edges = [
                e for e in self.G.edges(
                    self.G.nbunch_iter(
                        [node] + list(self.G.predecessors(node))),
                    data=True)
                if e[1] == node and e != edge]
            self.predecessor_edges.sort(
                key=lambda x: x[2]['weight'])
        next_edge = self.predecessor_edges[-1]
        self.predecessor_edges.pop(-1)
        return next_edge

    @staticmethod
    def _edge_extract(edge):
        return np.array(edge[2]['res_cost'])
