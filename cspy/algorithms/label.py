import types


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

    def dominates(self, other, direction):
        # Determine whether self dominates other. Returns bool
        if self.node != other.node:
            raise Exception("Non-comparable labels given")
        else:
            # Assume self dominates other
            if self.weight > other.weight:
                return False
            if direction == "forward":
                if any(self.res > other.res):
                    return False
            elif direction == "backward":
                # Check for the monotone resource (non-increasing)
                if self.res[0] < other.res[0]:
                    return False
                # Check for all other resources (non-decreasing)
                if any(self.res[1:] > other.res[1:]):
                    return False
            return True

    def get_new_label(self, edge, direction):
        path = list(self.path)
        weight, res = edge[2]["weight"], edge[2]["res_cost"]
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
                res_new = self.res + res
                res_new[0] = self.res[0] - 1
            else:
                res_new = self._REF_backward(self.res, edge)

        _new_label = Label(weight + self.weight, node, res_new, path)
        if _new_label == self:
            # If resulting label is the same
            return None
        return _new_label

    def feasibility_check(self, max_res, min_res):
        return all(max_res >= self.res) and all(min_res <= self.res)
