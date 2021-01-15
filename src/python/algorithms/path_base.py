from operator import add
from collections import deque
from logging import getLogger
from types import BuiltinFunctionType
from itertools import filterfalse, tee, chain

from numpy import zeros, array
from networkx import (shortest_simple_paths, astar_path, negative_edge_cycle)

from cspy.checking import check
from cspy.preprocessing import preprocess_graph

LOG = getLogger(__name__)


class PathBase:
    """
    Parent class for :class:Tabu, :class:GRASP, :class:GreedyElim,
    and :class:PSOLGENT.

    Contains path specific functionalitites.
    e.g. shortest path, feasibility checks, compatible joining
    """

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 preprocess,
                 threshold,
                 REF_callback,
                 algorithm=None):
        # Check inputs
        check(G,
              max_res,
              min_res,
              REF_callback=REF_callback,
              algorithm=__name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF_callback)

        self.max_res = max_res
        self.min_res = min_res
        self.threshold = threshold
        # Update resource extension function if given
        self.REF = REF_callback.REF_fwd if REF_callback is not None else add
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
        return astar_path(self.G, source, "Sink")

    def get_simple_path(self, source, max_depth):
        """Iterate through some paths (hopefully) and return the first one
        with total cost <= {0 or threshold} if a threshold specified.
        Otherwise, stops whenever max_depth is exceeded or all paths are
        inspected, whichever occurs first. In this case, the path with lowest
        cost is returned.
        """
        depth = 0

        # Create two copies of the simple path generator
        paths, paths_backup = tee(shortest_simple_paths(self.G, source, 'Sink'),
                                  2)
        paths_reduced = True

        # Select paths with under threshold if they exist
        try:
            cost_min = self.threshold if self.threshold is not None else 0
            paths_backup = filterfalse(
                lambda p: sum(self.G[i][j]["weight"]
                              for i, j in zip(p, p[1:])) >= cost_min,
                paths_backup)
            first = paths_backup.__next__()
            # add first element back
            paths = chain([first], paths_backup)
        except StopIteration:
            # if there are no paths under threshold or no paths with -ve cost
            cost_min = self.threshold if self.threshold is not None else 1e10
            paths_reduced = False
        except KeyError:
            return

        for p in paths:
            c = sum(self.G[i][j]["weight"] for i, j in zip(p, p[1:]))
            if c <= cost_min:
                if not paths_reduced:
                    _path = p
                    cost_min = c
                else:
                    return p
            if depth > max_depth:
                return _path
            depth += 1
        return _path

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
        shortest_path_edges = deque(iter(zip(self.st_path, self.st_path[1:])))
        shortest_path_edges_w_data = deque()
        shortest_path_edges_w_data.extend([
            (e[0], e[1], self.G[e[0]][e[1]]) for e in shortest_path_edges
        ])
        # init total resources and cost
        total_res = zeros(self.G.graph['n_res'])
        cost = 0
        # Check path for resource feasibility by adding one edge at a time
        for edge in shortest_path_edges_w_data:
            cost += edge[2]['weight']
            if isinstance(self.REF, BuiltinFunctionType):
                total_res += self._edge_extract(edge)
            else:
                total_res = self.REF(total_res, edge[0], edge[1],
                                     edge[2]["res_cost"], None, None)
                total_res = array(total_res)
            if not ((all(total_res <= self.max_res) and
                     all(total_res >= self.min_res))):
                break
        else:
            # Fesible path found. Save attributes.
            self.save(total_res, cost)
            return True
        # Return infeasible edge unless specified
        if return_edge:
            return edge
        else:
            return False

    def remove_edge(self, edge):
        if edge[:2] in self.G.edges():
            LOG.debug("Removed edge {}".format(edge[:2]))
            self.G.remove_edge(*edge[:2])

    def add_edge_back(self, edge):
        LOG.debug("Added edge back {}".format(edge[:2]))
        if "data" in edge[2]:
            self.G.add_edge(*edge[:2],
                            res_cost=edge[2]['res_cost'],
                            weight=edge[2]['weight'],
                            data=edge[2]['data'])
        else:
            self.G.add_edge(*edge[:2],
                            res_cost=edge[2]['res_cost'],
                            weight=edge[2]['weight'])

    def save(self, total_res, cost):
        if not self.threshold or (self.threshold is not None and
                                  cost <= self.threshold):
            self.best_path = self.st_path
            self.best_path_total_res = total_res
            self.best_path_cost = cost

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])
