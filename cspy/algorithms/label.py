from types import BuiltinFunctionType
from typing import List
from numpy import array_equal


class Label(object):
    """
    Label object that allows comparison and the modelling of dominance
    relations.

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

    REF_forward, REF_backward = None, None

    def __init__(self, weight: float, node: str, res: List, path: List):
        self.weight = weight
        self.node = node
        self.res = res
        self.path = path
        self.seen = False

    def __eq__(self, other):
        if other:
            if self.weight != other.weight:
                return False
            if self.node != other.node:
                return False
            if not array_equal(self.res, other.res):
                return False
            if self.path != other.path:
                return False
            return True
        return False

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Label({0},{1},{2})".format(self.weight, self.node, self.res)

    def dominates(self, other, direction: str) -> bool:
        """Determine whether `self` dominates `other`.
        :return: bool
        """
        if self.node != other.node:
            raise TypeError("Non-comparable labels given")

        # Assume self dominates other
        if self.weight > other.weight:
            return False
        if direction == "backward":
            # Check for the monotone resource (non-increasing)
            if self.res[0] < other.res[0]:
                return False
            # Check for all other resources (non-decreasing)
            if any(self.res[1:] > other.res[1:]):
                return False
        elif direction == "forward":
            if any(self.res > other.res):
                return False
        return True

    def full_dominance(self, other, direction: str) -> bool:
        """Checks whether `self` dominates `other` for the input direction.
        In the case when neither dominates , i.e. they are non-dominated,
        the direction is flipped labels are compared again.

        :return: bool
        """
        self_dominates = self.dominates(other, direction)
        other_dominates = other.dominates(self, direction)
        # self dominates other for the input direction
        if self_dominates:
            return True
        # Both non-dominated labels in this direction.
        elif (not self_dominates and not other_dominates):
            # flip directions
            flip_direc = "forward" if direction == "backward" else "backward"
            self_dominates_flipped = self.dominates(other, flip_direc)
            # label 1 dominates other in the flipped direction
            if self_dominates_flipped:
                return True
            elif self.weight < other.weight:
                return True

    def get_new_label(self, edge: tuple, direction: str):
        """Create a label by extending the current label along the input `edge`
        and `direction`.
        :return: new Label object.
        """
        path = list(self.path)
        weight, res = edge[2]["weight"], edge[2]["res_cost"]
        node = edge[1] if direction == "forward" else edge[0]
        if node in path:  # If node already visited.
            return None
        path.append(node)
        if direction == "forward":
            if isinstance(self.REF_forward, BuiltinFunctionType):
                res_new = self.res + res
            else:
                res_new = self.REF_forward(self.res, edge)
        elif direction == "backward":
            if isinstance(self.REF_backward, BuiltinFunctionType):
                res_new = self.res + res
                res_new[0] = self.res[0] - 1
            else:
                res_new = self.REF_backward(self.res, edge)

        _new_label = Label(weight + self.weight, node, res_new, path)
        if _new_label == self:
            # If resulting label is the same
            return None
        return _new_label

    def feasibility_check(self, max_res: List, min_res: List) -> bool:
        """Check whether `self` satisfies resource constraints for input
        `max_res` - Upper bound
        `min_res` - Lower bound
        :return: True if resource feasible label, False otherwise.
        """
        return all(max_res >= self.res) and all(min_res <= self.res)

    def subset(self, other) -> bool:
        """Determine whether all the nodes in the path of `other` are contained
        in `self`
        :return: True if input label is subset of current label, False otherwise.
        """
        return all(n in self.path for n in other.path)
