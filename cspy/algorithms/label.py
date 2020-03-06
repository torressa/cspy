import types
from numpy import equal
from operator import add, sub


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
        all nodes in the path
    """

    _REF_forward, _REF_backward = add, sub

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
        return (self.weight < other.weight and all(self.res <= other.res)) or (
            self.weight <= other.weight and
            (all(self.res <= other.res) and any(self.res < other.res)))

    def __le__(self, other):
        # Less than or equal to operator for two Label objects
        return self.weight <= other.weight and all(self.res <= other.res)

    def __eq__(self, other):
        # Equality operator for two Label objects
        if other:
            return (self.weight == other.weight and
                    all(equal(self.res, other.res)) and self.node == other.node)
        else:
            return False

    def __hash__(self):
        # Redefinition of hash to avoid TypeError due to the __eq__ definition
        return id(self)

    def dominates(self, other, direction):
        # Return whether self dominates other.
        if self.node != other.node:
            raise Exception("Non-comparable labels given")
        else:
            if direction == "forward":
                return (((self.weight < other.weight and
                          all(self.res <= other.res)) or
                         (self.weight <= other.weight and
                          (all(self.res <= other.res) and
                           any(self.res < other.res)))))
            elif direction == "backward":
                return (((self.weight < other.weight and
                          all(self.res >= other.res)) or
                         (self.weight <= other.weight and
                          (all(self.res >= other.res) and
                           any(self.res > other.res)))))
            else:
                raise Exception(
                    "{} cannot be used as a direction".format(direction))

    # @staticmethod
    def get_new_label(self, edge, direction, weight, res):
        # self = copy(self)
        path = list(self.path)
        node = edge[1] if direction == "forward" else edge[0]
        if node in path:  # If node already visited.
            return None
        else:
            path.append(node)
        if direction == "forward":
            if isinstance(self._REF_forward, types.BuiltinFunctionType):
                res_new = self.res + res
            else:
                res_new = self._REF_forward(self.res, edge)
        elif direction == "backward":
            if isinstance(self._REF_backward, types.BuiltinFunctionType):
                res_new = self.res - res
            else:
                res_new = self._REF_backward(self.res, edge)
        else:
            raise Exception(
                "{} cannot be used as a direction".format(direction))
        _new_label = Label(weight + self.weight, node, res_new, path)
        if _new_label == self:
            # If resulting label is the same
            return None
        return _new_label

    def feasibility_check(self, max_res, min_res):
        return all(max_res >= self.res) and all(min_res <= self.res)
