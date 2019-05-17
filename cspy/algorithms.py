''' Constrained Shortest Path Algorithm.
Implementation of the bidirectional algorithm for directed weighted graphs with
resource considerations from [1].
AUTHOR: David Torres, 2019 <d.torressanchez@lancs.ac.uk>
REFERENCES:
[1]  :  Tilk et al. (2017) Asymmetry matters: Dynamic half-way points in
        bidirectional labeling for solving shortest path problems with resource
        constraints faster. EJOR
[2]  :  Righini, G. , & Salani, M. (2006). Symmetry helps: Bounded
        bi-directional dynamic programming for the elementary shortest path
        problem with resource constraints.
        Discrete Optimization, 3 (3), 255-273 .
'''
from __future__ import absolute_import
from __future__ import print_function


import random
import logging
from collections import OrderedDict
from cspy.label import Label
from cspy.preprocessing import preprocess


class expand:
    pass


class BiDirectional:
    '''Bidirectional labeling algorithm with dynamic half-way point from [1].
    Depending on the range of values for self.HF = HF and self.HB = HB, we get
    four different algorithms.
    (1) If HF = HB > U:
        monodirectional forward labeling algorithm;
    (2) If HF = HB in (L, U):
        bidirectional labeling algorithm with static half-way point;
    (3) If HF = HB < L:
        monodirectional backward labeling algorithm;
    (4) If U = HF > HB = L then
        bidirectional labeling algorithm with dynamic half-way point.
    PARAMS
        G :: Digraph;
        L :: float, lower bound for resource usage;
        U :: float, upper bound for resource usage.
    '''

    def __init__(self, G, L, U):
        self.it = 0
        self.G = preprocess(G)  # call preprocessing function
        self.L, self.U = L, U
        self.HB = L  # type: float
        self.HF = U  # type: float

        self.nameAlgorithm()

        n_edges, n_res = len(G.edges()), G.graph['n_res']

        self.F, self.B = expand(), expand()
        self.F.Label = Label(0, 'Source', [0] * n_res, ['Source'])
        self.B.Label = Label(0, 'Sink', [n_edges + 1] * n_res, ['Sink'])
        self.F.unprocessed, self.B.unprocessed = {}, {}
        self.finalFpath, self.finalBpath = [], []

    def run(self):
        while self.F.Label or self.B.Label:
            self.stop = True
            direction = self.getDirection()
            if direction == 'forward':  # forward
                if self.F.Label.res[0] <= self.HF:
                    self.forwardAlg()
            elif direction == 'backward':
                if self.B.Label.res[0] > self.HB:
                    self.backwardAlg()
            else:
                break
            if (self.finalFpath and self.finalBpath and
                    (self.finalFpath[-1] == self.finalBpath[-1])):
                break
            self.checkDominance(direction)
            self.it += 1
        return self.joinPaths()

    #############
    # DIRECTION #
    #############
    def getDirection(self):
        if self.F.Label and not self.B.Label:
            return 'forward'
        elif not self.F.Label and self.B.Label:
            return 'backward'
        elif self.F.Label and self.B.Label:
            # return 'forward'
            return random.choice(['forward', 'backward'])
        else:  # if both are empty
            return

    #####################
    # FORWARD EXTENSION #
    #####################
    def forwardAlg(self):

        def _progateFlabel(edge):
            # Label propagation #
            weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
            new_label = self.F.Label.getNewLabel(
                'forward', weight, edge[1], res_cost)
            if new_label.res[0] <= self.HF:  # feasibility check
                self.F.unprocessed[self.F.Label][new_label] = new_label.path

        if self.F.Label not in self.F.unprocessed:
            self.F.unprocessed[self.F.Label] = {}
        edges = [e for e in self.G.edges(data=True)
                 if e[0] == self.F.Label.node]
        list(map(_progateFlabel, edges))
        self.HB = max(self.HB, min(self.F.Label.res[0], self.HF))
        self.getNextFlabel()

    ######################
    # BACKWARD EXTENSION #
    ######################
    def backwardAlg(self):

        def _progateBlabel(edge):
            # Label propagation #
            weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
            new_label = self.B.Label.getNewLabel(
                'backward', weight, edge[0], res_cost)
            if new_label.res[0] > self.HB:  # feasibility check
                self.B.unprocessed[self.B.Label][new_label] = new_label.path

        if self.B.Label not in self.B.unprocessed:
            self.B.unprocessed[self.B.Label] = {}
        edges = [e for e in self.G.edges(data=True)
                 if e[1] == self.B.Label.node]
        list(map(_progateBlabel, edges))
        self.HF = min(self.HF, max(self.B.Label.res[0], self.HB))
        self.getNextBlabel()

    ###################
    # LABEL RETRIEVAL #
    ###################
    # Forward
    def getNextFlabel(self):
        # Update next forward label with one with least weight
        if all(not val.keys() for key, val in self.F.unprocessed.items()):
            last_label = min(self.F.unprocessed.keys(), key=lambda x: x.weight)
            self.finalFpath = last_label.path
            self.F.Label = None
            return
        for key, val in self.F.unprocessed.items():
            if val:
                next_label = min(val.keys(), key=lambda x: x.weight)
                self.F.unprocessed[key].pop(next_label)
                self.F.Label = next_label
                break

    # Backward
    def getNextBlabel(self):
        if all(not val.keys() for key, val in self.B.unprocessed.items()):
            last_label = min(self.B.unprocessed.keys(), key=lambda x: x.weight)
            self.finalBpath = last_label.path
            self.B.Label = None
            print("entered")
            print(self.B.Label)
            return
        for key, val in self.B.unprocessed.items():
            if val:
                next_label = min(val.keys(), key=lambda x: x.weight)
                self.B.unprocessed[key].pop(next_label)
                self.B.Label = next_label
                break

    #############
    # DOMINANCE #
    #############
    def checkDominance(self, direction):

        def _dominanceF():
            # Forward
            for sub_dict in [d for d in self.F.unprocessed.values()
                             if self.F.Label in d]:
                for label in sub_dict.keys():
                    if label.dominates(self.F.Label, direction):
                        self.F.unprocessed[sub_dict].pop(self.F.Label)
                        self.F.unprocessed.pop(self.F.Label)
                        break

        def _dominanceB():
            # Backward
            for sub_dict in [d for d in self.B.unprocessed.values()
                             if self.B.Label in d]:
                for label in sub_dict.keys():
                    if label.dominates(self.B.Label, direction):
                        self.B.unprocessed[sub_dict].pop(self.B.Label)
                        self.B.unprocessed.pop(self.B.Label)
                        break

        print('FORWARD unprocessed')
        print(self.F.unprocessed)
        print(self.F.Label)
        print('Backward unprocessed')
        print(self.B.unprocessed)
        print(self.B.Label)
        print('\n')
        if direction == 'forward':
            if self.F.Label:
                _dominanceF()
        else:
            if self.B.Label:
                _dominanceB()

    #################
    # PATH CHECKING #
    #################
    def joinPaths(self):
        # check if paths are eligible to be joined. Joining phase as presented
        # in [2]
        def _checkPaths():
            if (self.finalFpath[-1] == 'Sink' and  # if only forward path
                    self.finalBpath[0] != 'Source'):
                return self.finalFpath
            elif (self.finalBpath[0] == 'Source' and  # if only backward path
                  self.finalFpath[-1] != 'Sink'):
                return self.finalBpath
            elif (self.finalBpath[0] == 'Source' and  # if both full paths
                  self.finalFpath[-1] == 'Sink'):
                return random.choice([self.finalFpath, self.finalBpath])
            else:  # if combination of the two is required
                return list(OrderedDict.fromkeys(
                    self.finalFpath + self.finalBpath))

        self.finalBpath.reverse()  # reverse order for backward path
        joined_path = _checkPaths()
        logging.info(joined_path)
        return joined_path

    def nameAlgorithm(self):
        if self.HF == self.HB > self.U:
            logging.info('Monodirectional forward labeling algorithm')
        elif self.L < self.HF == self.HB < self.U:
            logging.info(
                'bidirectional labeling algorithm with static halfway point')
        elif self.HF == self.HB < self.L:
            logging.info('monodirectional backward labeling algorithm')
        elif self.U == self.HF > self.HB == self.L:
            logging.info('bidirectional labeling algorithm with dynamic' +
                         ' halfway point.')
