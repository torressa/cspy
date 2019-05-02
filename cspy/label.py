from operator import add, sub


class Label(object):

    def __init__(self, weight, node, res, path):
        self.weight = weight  # cumulative edge weight
        self.node = node  # current node
        self.res = res  # cumulative resource consumption
        self.path = path  # corresponding path

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "Label({0},{1},{2})".format(self.node, self.weight, self.res)

    def __lt__(self, other):
        # Less than operator for two Label objects
        return self.weight < other.weight and self.res <= other.res

    def __le__(self, other):
        # Less than or equal to operator for two Label objects
        return self.weight <= other.weight and self.res <= other.res

    def __eq__(self, other):
        # Equality operator for two Label objects
        return self.weight == other.weight and self.res == other.res

    def __hash__(self):
        # Redefinition of hash to avoid TypeError due to the __eq__ definition
        return id(self)

    def dominates(self, other):
        # Return whether self dominates other.
        return self < other

    def getNewLabel(self, direction, weight, node, res):
        path = list(self.path)
        path.append(node)
        if direction == 'forward':
            res_new = list(map(add, self.res, res))
        else:
            res_new = list(map(sub, self.res, res))
        return Label(weight + self.weight, node, res_new, path)
