from numpy import zeros, array


class Path(object):
    """docstring for Path"""

    def __init__(self, G, path, max_res, min_res):
        self.G = G
        self.path = path
        self.max_res = max_res
        self.min_res = min_res

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "Path({0},{1},{2})".format(
            self.path, self.max_res, self.min_res)

    def _check_feasibility(self):
        shortest_path_edges = (
            edge for edge in self.G.edges(
                self.G.nbunch_iter(self.path), data=True)
            if edge[0:2] in zip(self.path, self.path[1:])
        )
        total_res = zeros(self.G.graph['n_res'])
        # Check path for resource feasibility by adding one edge at a time
        for edge in shortest_path_edges:
            total_res += self._edge_extract(edge)
            if (all(total_res <= self.max_res) and
                    all(total_res >= self.min_res)):
                pass
            else:
                break
        else:
            return True
        return edge

    @staticmethod
    def _edge_extract(edge):
        return array(edge[2]['res_cost'])
