from __future__ import absolute_import
from __future__ import print_function

import logging
import numpy as np
import networkx as nx
from cspy.label import Label
from cspy.preprocessing import check


class Tabu:
    """Heuristic Tabu search algorithm for the (resource) constrained shortest
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
    To run the algorithm, create a :class:`Tabu` instance and call `run`.

    .. code-block:: python

        >>> from cspy import Tabu
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
        >>> path = Tabu(G, max_res, min_res).run()
        >>> print(path)
        ['Source', 'A', 'B', 'C', 'Sink']

    """

    def __init__(self, G, max_res, min_res):
        # Input parameters
        check(G, max_res, min_res)
        self.G = G
        self.max_res = max_res
        self.min_res = min_res
        # Algorithm specific parameters
        self.it = 0
        self.path = []
        self.stop = False
        self.H = self.G.copy()  # subgraph
        self.predecessor_edges = []
        self.edges_to_remove = dict(self.G.edges())
        # Import function from cspy.label.Label
        self.check_feasibility = Label.check_geq

    def run(self):
        """Runs Tabu Search with resource constraints for the input graph"""
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
            path = nx.astar_path(self.H, 'Source', 'Sink')
        except nx.NetworkXException:
            pass
        self.H = self.G.copy()  # subgraph
        if path:
            shortest_path_edges = (edge for edge in
                                   self.G.edges(
                                       self.G.nbunch_iter(path), data=True)
                                   if edge[0:2] in zip(path, path[1:]))
            total_res = np.zeros(self.G.graph['n_res'])
            for edge in shortest_path_edges:
                total_res += self._edge_extract(edge)
                if (self.check_feasibility(self.max_res, total_res) and
                        self.check_feasibility(total_res, self.min_res)):
                    pass
                else:
                    self._update_graph(edge)
                    break
            else:
                self.path = path
                self.stop = True
        else:
            self._update_graph()

    def _update_graph(self, edge=None):
        if self.it == 0:
            self.last_edge_removed = edge
        if self.predecessor_edges:
            edge_to_remove = self.next_predecessor_edge()
        else:
            if self.edges_to_remove:
                self.get_predecessor_edges(self.last_edge_removed)
                if edge and edge[:2] in self.edges_to_remove:
                    edge_to_remove = edge
                elif self.predecessor_edges:
                    edge_to_remove = self.next_predecessor_edge()
                else:
                    self.stop = True
                    return
            else:
                self.stop = True
                return
        self.edges_to_remove.pop(edge_to_remove[:2], None)
        self.H.remove_edge(*edge_to_remove[:2])
        self.last_edge_removed = edge_to_remove

    def get_predecessor_edges(self, edge):
        node = edge[0]
        self.predecessor_edges = [
            e for e in self.G.edges(
                self.G.nbunch_iter([node] + list(self.G.predecessors(node))),
                data=True)
            if e[1] == node and e != edge]
        self.predecessor_edges.sort(
            key=lambda x: x[2]['weight'])

    def next_predecessor_edge(self):
        """Retrieves the edge adjacent to node with the largest weight"""
        next_edge = self.predecessor_edges[-1]
        self.predecessor_edges.pop(-1)
        return next_edge

    @staticmethod
    def _edge_extract(edge):
        return np.array(edge[2]['res_cost'])
