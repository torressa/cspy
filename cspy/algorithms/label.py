from typing import List, Callable
from types import BuiltinFunctionType

from numpy import greater, greater_equal, less_equal


class Label:
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

    REF_forward: Callable = None
    REF_backward: Callable = None

    def __init__(self, weight: float, node: str, res: List, path: List):
        self.weight = weight
        self.node = node
        self.res = res
        self.path = path

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Label({0},{1})".format(self.weight, self.path)

    def get_new_label(self, edge: tuple, direction: str):
        """Create a label by extending the current label along the input `edge`
        and `direction`.
        :return: new Label object.
        """
        path = list(self.path)
        weight, res = edge[2]["weight"], edge[2]["res_cost"]
        node = edge[1] if direction == "forward" else edge[0]
        # FIXME hardcoded elementary
        if node in path:  # If node already visited.
            return None
        path.append(node)
        if direction == "forward":
            if isinstance(self.REF_forward, BuiltinFunctionType):
                res_new = self.res + res
            else:
                res_new = self.REF_forward(self.res,
                                           edge,
                                           partial_path=self.path,
                                           accumulated_cost=self.weight)

        elif direction == "backward":
            if isinstance(self.REF_backward, BuiltinFunctionType):
                res_new = self.res + res
                res_new[0] = self.res[0] - 1
            else:
                res_new = self.REF_backward(self.res,
                                            edge,
                                            partial_path=self.path,
                                            accumulated_cost=self.weight)

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
        return all(greater_equal(max_res, self.res)) and all(
            less_equal(min_res, self.res))

    def dominates(self, other, direction: str) -> bool:
        """Determine whether `self` dominates `other`.
        :return: bool
        """
        # Assume self dominates other
        if self.node != other.node:
            raise TypeError("Non-comparable labels given")

        if self.weight > other.weight:
            return False
        if direction == "backward":
            # Check for the monotone resource (non-increasing)
            if self.res[0] < other.res[0]:
                return False
            # Check for all other resources (non-decreasing)
            if any(greater(self.res[1:], other.res[1:])):
                return False
        elif direction == "forward":
            if any(greater(self.res, other.res)):
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

    def check_threshold(self, threshold) -> bool:
        """Check if a s-t path has a total weight
        is under the threshold."""
        return self.weight <= threshold

    def check_st_path(self) -> bool:
        return ((self.path[0] == "Source" and self.path[-1] == "Sink") or
                (self.path[-1] == "Source" and self.path[0] == "Sink"))
