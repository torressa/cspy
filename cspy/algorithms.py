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
from cspy.preprocessing import preprocess, check_inputs


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
        max_res :: list of floats, [L, M_1, M_2, ..., M_nres]
                    upper bound for resource usage;
        min_res :: list of floats, [U, L_1, L_2, ..., L_nres]
                    lower bounds for resource usage.
    '''

    def __init__(self, G, max_res, min_res):

        check_inputs(max_res, min_res)

        # call preprocessing function
        self.G, _ = preprocess(G, max_res, min_res)
        self.max_res, self.min_res = max_res, min_res
        self.L, self.U = self.max_res[0], self.min_res[0]
        self.HB = self.L  # type: float
        self.HF = self.U  # type: float

        self.nameAlgorithm()

        n_edges, n_res = len(G.edges()), G.graph['n_res']

        self.Label = {
            # init current forward label
            'forward': Label(0, 'Source', [0] * n_res, ['Source']),
            # init current backward label
            'backward': Label(0, 'Sink', [n_edges + 1] * n_res, ['Sink'])}

        # init forward and backward unprocessed labels
        self.unprocessed = {}
        self.unprocessed['forward'], self.unprocessed['backward'] = {}, {}
        # init final path
        self.finalpath = {}
        self.finalpath['forward'], self.finalpath['backward'] = [], []

    def run(self):
        while self.Label['forward'] or self.Label['backward']:
            direc = self.getDirection()
            if direc:
                self.algorithm(direc)
                self.checkDominance(direc)
            else:
                break
            if (self.finalpath['forward'] and self.finalpath['backward'] and
                    (self.finalpath['forward'][-1] ==
                        self.finalpath['backward'][-1])):
                break
        return self.joinPaths()

    #############
    # DIRECTION #
    #############
    def getDirection(self):
        if self.Label['forward'] and not self.Label['backward']:
            return 'forward'
        elif not self.Label['forward'] and self.Label['backward']:
            return 'backward'
        elif self.Label['forward'] and self.Label['backward']:
            return random.choice(['forward', 'backward'])
        else:  # if both are empty
            return

    #############
    # ALGORITHM #
    #############

    def algorithm(self, direc):

        def _progateLabel(edge):
            # Label propagation #
            weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
            node = edge[1] if direc == 'forward' else edge[0]
            new_label = self.Label[direc].getNewLabel(
                direc, weight, node, res_cost)
            if direc == 'forward':
                if new_label.res <= self.max_res:  # feasibility check
                    self.unprocessed[direc][self.Label[direc]][
                        new_label] = new_label.path
            else:
                if new_label.res > self.min_res:  # feasibility check
                    self.unprocessed[direc][self.Label[direc]][
                        new_label] = new_label.path

        def _getNextLabel():
            # Label Extension #
            keys_to_pop = []
            for key, val in self.unprocessed[direc].items():
                if val:
                    # Update next forward label with one with least weight
                    next_label = min(val.keys(), key=lambda x: x.weight)
                    # Remove it from the unprocessed labels
                    self.unprocessed[direc][key].pop(next_label)
                    self.Label[direc] = next_label
                    break
                else:
                    keys_to_pop.extend([self.Label[direc], key])
            else:   # if no break
                # Update last forward label with one with least weight
                last_label = min(self.unprocessed[direc].keys(),
                                 key=lambda x: x.weight)
                self.finalpath[direc] = last_label.path
                keys_to_pop.append(last_label)
                self.Label[direc] = None
            for k in keys_to_pop:
                self.unprocessed[direc].pop(k, None)
            if not self.finalpath[direc]:
                self.finalpath[direc] = self.Label[direc].path

        if direc == 'forward':  # forward
            if not self.Label[direc].res <= self.max_res:
                return
            edges = [e for e in self.G.edges(data=True)
                     if e[0] == self.Label[direc].node]
            self.min_res[0] = max(self.min_res[0], min(
                self.Label[direc].res[0], self.max_res[0]))
        else:  # backward
            if not self.Label[direc].res > self.min_res:
                return
            edges = [e for e in self.G.edges(data=True)
                     if e[1] == self.Label[direc].node]
            self.max_res[0] = min(self.max_res[0], max(
                self.Label[direc].res[0], self.min_res[0]))

        if self.Label[direc] not in self.unprocessed[direc]:
            self.unprocessed[direc][self.Label[direc]] = {}

        list(map(_progateLabel, edges))
        _getNextLabel()

    #############
    # DOMINANCE #
    #############
    def checkDominance(self, direc):
        for sub_dict in [d for d in self.unprocessed[direc].values()
                         if self.Label[direc] in d]:
            for label in sub_dict.keys():
                if label.dominates(self.Label[direc]):
                    self.unprocessed[direc][sub_dict].pop(
                        self.Label[direc], None)
                    self.unprocessed[direc].pop(self.Label[direc], None)
                elif self.Label[direc].dominates(label):
                    self.unprocessed[direc][sub_dict].pop(label, None)
                    self.unprocessed[direc].pop(label, None)

    #################
    # PATH CHECKING #
    #################
    def joinPaths(self):
        # check if paths are eligible to be joined. Joining phase as presented
        # in [2]
        def _checkPaths():
            if (self.finalpath['forward'][-1] == 'Sink' and
                    self.finalpath['backward'][0] != 'Source'):
                # if only backward path
                return self.finalpath['forward']
            elif (self.finalpath['backward'][0] == 'Source' and
                  self.finalpath['forward'][-1] != 'Sink'):
                # if only backward path
                return self.finalpath['backward']
            elif (self.finalpath['backward'][0] == 'Source' and
                  self.finalpath['forward'][-1] == 'Sink'):
                # if both full paths
                return random.choice(
                    [self.finalpath['forward'], self.finalpath['backward']])
            elif not self.Label['forward'] or not self.Label['backward']:
                # if combination of the two is required
                return list(OrderedDict.fromkeys(
                    self.finalpath['forward'] + self.finalpath['backward']))
            else:
                return

        if self.finalpath['forward'] and self.finalpath['backward']:
            # reverse order for backward path
            self.finalpath['backward'].reverse()
            joined_path = _checkPaths()
            logging.info(joined_path)
            return joined_path
        else:
            return

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
