from operator import add
from collections import deque
from logging import getLogger
from numpy import zeros, array
from types import BuiltinFunctionType
from itertools import filterfalse, tee, chain
from networkx import (shortest_simple_paths, astar_path, negative_edge_cycle)

from cspy.checking import check
from cspy.preprocessing import preprocess_graph

log = getLogger(__name__)


class PathBase(object):
    """
    Parent class for :class:Tabu, :class:GRASP, :class:GreedyElim,
    and :class:PSOLGENT.

    Contains path specific functionalitites.
    e.g. shortest path, feasibility checks, compatible joining
    """

    def __init__(self, G, max_res, min_res, preprocess, REF, algorithm=None):
        # Check inputs
        check(G, max_res, min_res, REF_forward=REF, algorithm=__name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF)

        self.max_res = max_res
        self.min_res = min_res
        # Update resource extension function if given
        if REF:
            self.REF = REF
        else:
            self.REF = add

        if negative_edge_cycle(G) or algorithm == "simple":
            self.algorithm = "simple"
        else:
            self.algorithm = "astar"

        # Attribute to hold source-sink path
        self.st_path = None

        # Attribrutes for exposure #
        # resource feasible source-sink path
        self.best_path = None
        # Final cost
        self.best_path_cost = None
        # Final resource consumption
        self.best_path_total_res = None

    @property
    def path(self):
        """
        Get list with nodes in calculated path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path

    @property
    def total_cost(self):
        """
        Get accumulated cost along the path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path_cost

    @property
    def consumed_resources(self):
        """
        Get accumulated resources consumed along the path.
        """
        if not self.best_path:
            raise Exception("Please call the .run() method first")
        return self.best_path_total_res

    def get_shortest_path(self, source, max_depth):
        # Select appropriate shortest path algorithm
        if self.algorithm == "simple":
            return self.get_simple_path(source, max_depth)
        else:
            return astar_path(self.G, source, "Sink")

    def get_simple_path(self, source, max_depth):
        depth = 0

        # Create two copies of the simple path generator
        paths, paths_backup = tee(shortest_simple_paths(self.G, source, 'Sink'),
                                  2)

        # Select only paths with negative reduced cost if they exist
        try:
            cost_min = 0
            paths_backup = filterfalse(
                lambda p: sum(self.G[i][j]["weight"]
                              for i, j in zip(p, p[1:])) >= 0, paths_backup)
            first = paths_backup.__next__()
            # add first element back
            paths = chain([first], paths_backup)
        except StopIteration:
            # if there exist paths with negative cost
            cost_min = 1e10
        except KeyError:
            return

        for p in paths:
            c = sum(self.G[i][j]["weight"] for i, j in zip(p, p[1:]))
            if c < cost_min:
                path = p
                cost_min = c
            if depth > max_depth:
                return path
            depth += 1
        # All paths consumed
        return path

    def check_feasibility(self, return_edge=True):
        """
        Checks for feasibility for a valid source-sink path.
        If the path (in the st_path attribute) is feasible, then it
        returns true and saves the path, cost and total resources consumed in
        the process.
        Otherwise, by default, it returns the edge that makes the path
        infeasible.
        This can changed with the ``return_edge`` parameter.
        """
        shortest_path_edges = deque(
            e for e in zip(self.st_path, self.st_path[1:]))
        shortest_path_edges_w_data = deque()
        shortest_path_edges_w_data.extend([
            (e[0], e[1], self.G[e[0]][e[1]]) for e in shortest_path_edges
        ])
        # init total resources and cost
        total_res = zeros(self.G.graph['n_res'])
        _cost = 0
        # Check path for resource feasibility by adding one edge at a time
        for edge in shortest_path_edges_w_data:
            _cost += edge[2]['weight']
            if isinstance(self.REF, BuiltinFunctionType):
                total_res += self._edge_extract(edge)
            else:
                total_res = self.REF(total_res, edge)
            if (all(total_res <= self.max_res) and
                    all(total_res >= self.min_res)):
                pass
            else:
                break
        else:
            # Fesible path found. Save attributes.
            self.best_path = self.st_path
            self.best_path_total_res = total_res
            self.best_path_cost = _cost
            return True
        # Return infeasible edge unless specified
        if return_edge:
            return edge
        else:
            return False

    def remove_edge(self, edge):
        if edge[:2] in self.G.edges():
            log.debug("Removed edge {}".format(edge[:2]))
            self.G.remove_edge(*edge[:2])

    def add_edge_back(self, edge):
        log.debug("Added edge back {}".format(edge[:2]))
        if "data" in edge[2]:
            self.G.add_edge(*edge[:2],
                            res_cost=edge[2]['res_cost'],
                            weight=edge[2]['weight'],
                            data=edge[2]['data'])
        else:
            self.G.add_edge(*edge[:2],
                            res_cost=edge[2]['res_cost'],
                            weight=edge[2]['weight'])

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])
