#!/usr/bin/env pypy

# import networkx as nx
# from operator import add
from collections import OrderedDict


class expand(object):
    pass


class BiDirectional(object):
    ''' bidirectional labeling algorithm with dynamic half-way point.
    PARAMS
        G :: Digraph
        L :: float, lower bound for resource usage
        U :: float, upper bound for resource usage'''

    def __init__(self, G, L, U):
        self.G = G
        self.HB = L
        self.HF = U
        self.F, self.B = expand(), expand()
        self.F.label, self.B.label = 'Source', 'Sink'
        self.F.unprocessed, self.B.unprocessed = {}, {}
        self.F.res, self.B.res = 0, 50  # [0] * self.G.graph['n_res']
        self.F.path, self.B.path = [self.F.label], [self.B.label]

    def _run(self):
        check_dominance = True

        while self.F.label or self.B.label:
            direction = self._get_next_direction()
            if direction == 'forward':  # forward
                if self.F.res <= self.HF:
                    if self.F.label not in self.F.unprocessed.keys():
                        self.F.unprocessed[self.F.label] = []
                    edges = [e for e in self.G.edges(data=True)
                             if e[0] == self.F.label]
                    # edges = [(i, j) for j in self.G.successors_iter(i)]
                    for edge in edges:
                        res_cost = self.F.res + edge[2]['res_cost']
                        self.F.res = res_cost
                        # list(map(add, self.F.res, edge[2]['res_cost']))
                        if res_cost <= self.HF:
                            self.F.unprocessed[self.F.label].extend(
                                [(edge[1], res_cost)])
                    self.HB = max(self.HB, min(self.F.res, self.HF))
                    self._get_next_Flabel()
                    if self.F.label:
                        self.F.path.append(self.F.label)
                        if self.F.label == 'Sink':
                            break
            elif direction == 'backward':
                if self.B.res > self.HB:
                    if self.B.label not in self.B.unprocessed.keys():
                        self.B.unprocessed[self.B.label] = []
                    edges = [e for e in self.G.edges(data=True)
                             if e[1] == self.B.label]
                    for edge in edges:
                        res_cost = self.B.res - edge[2]['res_cost']
                        self.B.res = res_cost
                        # list(map(add, self.B.res, edge[2]['res_cost']))
                        if self.B.res > self.HB:
                            self.B.unprocessed[self.B.label].extend(
                                [(edge[0], res_cost)])
                    self.HF = min(self.HF, max(self.B.res, self.HB))
                    self._get_next_Blabel()
                    if self.B.label:
                        self.B.path.append(self.B.label)
                        if self.B.label == 'Source':
                            break
            else:
                break
            if check_dominance:
                self._check_dominance()
        return self._join_paths()

    def _get_next_direction(self):
        import random

        if self.F.label and not self.B.label:
            return 'forward'
        elif not self.F.label and self.B.label:
            return 'backward'
        elif self.F.label and self.B.label:
            # return 'forward'
            return random.choice(['forward', 'backward'])
        else:  # if both are empty
            return

    def _get_next_Flabel(self):
        if self.F.label in self.F.unprocessed.keys():
            labels = self.F.unprocessed[self.F.label]
            if len(labels) > 0:
                self.F.label = sorted(labels, key=lambda x: x[1])[0][0]
            else:
                self.F.label = None
        return

    def _get_next_Blabel(self):
        if self.B.label in self.B.unprocessed.keys():
            labels = self.B.unprocessed[self.B.label]
            if len(labels) > 0:
                self.B.label = sorted(labels, key=lambda x: x[
                                      1], reverse=True)[0][0]
            else:
                self.B.label = None
        return

    def _check_dominance(self):
        pass

    def _join_paths(self):
        self.B.path.reverse()  # reverse order for backward path
        print list(OrderedDict.fromkeys(self.F.path + self.B.path))
        return list(OrderedDict.fromkeys(self.F.path + self.B.path))
