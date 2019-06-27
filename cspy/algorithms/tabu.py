from __future__ import absolute_import
from __future__ import print_function

import logging
import numpy as np
import networkx as nx
from cspy.label import Label
from cspy.preprocessing import check


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
        :math:`[M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    min_res : list of floats
        :math:`[L_1, L_2, ..., L_{n\_res}]` lower bounds for resource usage.
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
        self.initial_path = []
        self.stop = False
        self.neighbour = 'Source'
        self.neighbourhood = []
        self.tabu_edge = None
        self.edges_to_check = dict(self.G.edges())
        # Import function from cspy.label.Label
        self.check_feasibility = Label.check_geq

    def run(self):
        """
        Runs Tabu Search with resource constraints for the input graph
        """
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
            path = nx.astar_path(self.G, self.neighbour,
                                 'Sink', heuristic=self.heuristic)
        except nx.NetworkXException:
            pass
        if path:
            self.update_path(path)
            shortest_path_edges = (
                edge for edge in self.G.edges(
                    self.G.nbunch_iter(self.path), data=True)
                if edge[0:2] in zip(self.path, self.path[1:]))
            total_res = np.zeros(self.G.graph['n_res'])
            # Check path for resource feasibility by adding one edge at a time
            for edge in shortest_path_edges:
                total_res += self._edge_extract(edge)
                if (self.check_feasibility(self.max_res, total_res) and
                        self.check_feasibility(total_res, self.min_res)):
                    pass
                else:
                    self._get_neighbour(edge)
                    break
            else:
                self.stop = True
        else:
            self._get_neighbour(self.tabu_edge)

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
            self.neighbourhood = [
                e for e in self.G.edges(
                    self.G.nbunch_iter(
                        [node] + list(self.G.predecessors(node))),
                    data=True)
                if e[1] == node and e != edge]
            self.neighbourhood.sort(
                key=lambda x: x[2]['weight'])
        next_edge = self.neighbourhood[-1]
        self.neighbourhood.pop(-1)
        return next_edge

    def update_path(self, path):
        if self.it == 0:
            self.initial_path = path
        if self.neighbour in self.initial_path:
            self.path = [node for node in self.initial_path
                         if (node != self.neighbour and
                             self.initial_path.index(node) <=
                             self.initial_path.index(self.neighbour))] + path
        else:
            self.merge_paths(path)

    def merge_paths(self, path):
        branch_path = list(set(self.initial_path).difference(path))
        for node in branch_path:
            if (node, self.neighbour) in self.G.edges():
                self.path = [n for n in branch_path
                             if (n == node and
                                 branch_path.index(n) <=
                                 branch_path.index(node))] + path
                break

    def heuristic(self, i, j):
        # Given a node pair returns a weight to apply
        if (i, j) == self.tabu_edge or not (i, j) in self.G.edges():
            return 1e10
        else:
            return self.G.get_edge_data(i, j)['weight']

    @staticmethod
    def _edge_extract(edge):
        return np.array(edge[2]['res_cost'])
