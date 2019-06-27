from operator import sub


class Label(object):
    """Label object that allows comparison and the modelling of dominance relations

    Parameters
    -----------

    weight : float
        cumulative edge weight

    node : string
        name of last node visited

    res : list
        cumulative edge resource consumption

    path : list
        all nodes in the path"""

    _REF_forward, _REF_backward = None, None

    def __init__(self, weight, node, res, path):
        self.weight = weight
        self.node = node
        self.res = res
        self.path = path

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "Label({0},{1},{2})".format(self.weight, self.node, self.res)

    def __lt__(self, other):
        # Less than operator for two Label objects
        return (self.weight < other.weight and self.res <= other.res) or (
            self.weight <= other.weight and self.res < other.res)

    def __le__(self, other):
        # Less than or equal to operator for two Label objects
        return self.weight <= other.weight and self.res <= other.res

    def __eq__(self, other):
        # Equality operator for two Label objects
        return (self.weight == other.weight and self.res == other.res and
                self.node == other.node)

    def __hash__(self):
        # Redefinition of hash to avoid TypeError due to the __eq__ definition
        return id(self)

    def dominates(self, other, direction="forward"):
        # Return whether self dominates other.
        if direction == 'forward':
            return self.node == other.node and (
                (self.weight < other.weight and self.res <= other.res) or (
                    self.weight <= other.weight and self.res < other.res))
        else:
            return self.node == other.node and (
                (self.weight < other.weight and self.res >= other.res) or (
                    self.weight <= other.weight and self.res > other.res))

    def get_new_label(self, direction, weight, node, res):
        path = list(self.path)
        path.append(node)
        if direction == 'forward':
            res_new = list(map(self._REF_forward, self.res, res))
        else:
            res_new = list(map(self._REF_backward, self.res, res))
        return Label(weight + self.weight, node, res_new, path)

    def feasibility_check(self, max_res=[], min_res=[],
                          direction="forward"):
        if direction == "forward":
            return self.check_geq(max_res, self.res)
        else:
            return self.check_geq(self.res, min_res, "gt")

    @staticmethod
    def check_geq(l1, l2, inequality="geq"):
        """Determines if all elements of list l1 either >=
        or > than those in list l2.

        Parameters
        ----------
        l1, l2 : list
            lists of integers.

        inequality : string, optional
            type of inequality 'ge' for >= 'gt' for >. Default: 'ge'
            """
        diff = list(map(sub, l1, l2))
        if inequality == "gt":
            return all(elem > 0 for elem in diff)
        else:
            return all(elem >= 0 for elem in diff)
