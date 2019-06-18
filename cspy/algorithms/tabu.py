from __future__ import absolute_import
from __future__ import print_function

import logging
import networkx as nx
from operator import add, sub


class Tabu:
    """docstring for MinimumDeviation"""

    def __init__(self, G, max_res, min_res):
        self.G = G  # check_and_preprocess(True, G, max_res, min_res, 'both')
        self.max_res = max_res
        self.min_res = min_res

    def run(self):
        while True:
            path = nx.astar_path(self.G, 'Source', 'Sink')
            shortest_path_edges = [edge for edge in self.G.edges(data=True)
                                   if edge[0:2] in zip(path, path[1:])]
            total_res = [0] * self.G.graph['n_res']
            for edge in shortest_path_edges:
                total_res = list(map(add, total_res, edge[2]['res_cost']))
                diff_max = list(map(sub, self.max_res, total_res))
                diff_min = list(map(sub, total_res, self.min_res))
                if (all(elem >= 0 for elem in diff_max) and
                        all(elem >= 0 for elem in diff_min)):
                    pass
                else:
                    logging.debug("[{}] Deleted edge {} -> {}".format(
                        __name__, edge[0], edge[1]))
                    logging.debug("[{}] Number of edges {}".format(
                        __name__, len(self.G.edges())))
                    self.G.remove_edge(*edge[:2])
                    break
            else:
                break
        if path:
            logging.debug(path)
            return path, shortest_path_edges
        else:
            raise Exception("No path found")
