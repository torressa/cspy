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
        Discrete Optimization, 3 (3), 255-273.
'''
from __future__ import absolute_import
from __future__ import print_function

import random
import logging
from operator import add, sub
from collections import OrderedDict
from cspy.label import Label
from cspy.preprocessing import check_and_preprocess


class expand:
    pass


class BiDirectional:
    """Bidirectional labeling algorithm with dynamic half-way point from [1].
    Depending on the range of values for self.HF = HF and self.HB = HB, we get
    four different algorithms. See self.name_algorithm.
    PARAMS
        G          :: nx.Digraph() object with n_res attribute;
        max_res    :: list of floats, [L, M_1, M_2, ..., M_nres]
                    upper bound for resource usage;
        min_res    :: list of floats, [U, L_1, L_2, ..., L_nres]
                    lower bounds for resource usage.
        direc_in   :: string, preferred search direction.
                    Either 'both','forward', or, 'backward'.
        preprocess :: bool, enables preprocessing routine."""

    def __init__(self, G, max_res=None, min_res=None, direc_in='both',
                 preprocess=True, REF_forward=add, REF_backward=sub,):

        self.G = check_and_preprocess(
            preprocess, G, max_res, min_res, direc_in)
        self.direc_in = direc_in
        self.max_res, self.min_res = max_res, min_res
        self.L, self.U = self.max_res[0], self.min_res[0]
        self.HB = self.L  # type: float
        self.HF = self.U  # type: float

        Label._REF_forward = REF_forward
        Label._REF_backward = REF_backward

        self.name_algorithm()

        n_res = G.graph['n_res']

        self.Label = {
            # init current forward label
            'forward': Label(0, 'Source', [0] * n_res, ['Source']),
            # init current backward label
            'backward': Label(0, 'Sink', max_res, ['Sink'])}

        # init forward and backward unprocessed labels
        self.unprocessed = dict()
        self.unprocessed['forward'], self.unprocessed['backward'] = {}, {}
        # init final path
        self.finalpath = dict()
        self.finalpath['forward'], self.finalpath['backward'] = [
            "Source"], ["Sink"]

    def run(self):
        while self.Label['forward'] or self.Label['backward']:
            direc = self.get_direction()
            if direc:
                self.algorithm(direc)
                self.check_dominance(direc)
            elif not direc or self.terminate(direc):
                break
        return self.join_paths()

    #############
    # DIRECTION #
    #############
    def get_direction(self):
        if self.direc_in == 'both':
            if self.Label['forward'] and not self.Label['backward']:
                return 'forward'
            elif not self.Label['forward'] and self.Label['backward']:
                return 'backward'
            elif self.Label['forward'] and self.Label['backward']:
                return random.choice(['forward', 'backward'])
            else:  # if both are empty
                return
        else:
            if not self.Label['forward'] and not self.Label['backward']:
                return
            elif not self.Label[self.direc_in]:
                return
            else:
                return self.direc_in

    #############
    # ALGORITHM #
    #############
    def algorithm(self, direc):

        def _propagate_label(edge):
            # Label propagation #
            weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
            node = edge[1] if direc == 'forward' else edge[0]
            new_label = self.Label[direc].get_new_label(
                direc, weight, node, res_cost)
            if new_label.feasibility_check(
                    self.max_res, self.min_res, direc):
                self.unprocessed[direc][self.Label[direc]][
                    new_label] = new_label.path

        def _get_next_label():
            # Label Extension #
            keys_to_pop = []
            for key, val in self.unprocessed[direc].items():
                if val:
                    # Update next forward label with one with least weight
                    next_label = min(val.keys(), key=lambda x: x.weight)
                    # Remove it from the unprocessed labels
                    self.unprocessed[direc][key].pop(next_label)
                    self.Label[direc] = next_label
                    if not self.unprocessed[direc][key]:
                        keys_to_pop.append(key)
                    break
                else:
                    keys_to_pop.extend([self.Label[direc], key])
            else:  # if no break
                next_label = min(
                    self.unprocessed[direc].keys(), key=lambda x: x.weight)
                # Remove it from the unprocessed labels
                keys_to_pop.append(next_label)
                if self.Label[direc] == next_label:
                    self.save_final_path(direc)
                    keys_to_pop.append(self.Label[direc])
                    self.Label[direc] = None
                else:
                    self.Label[direc] = next_label
            # Remove all processed labels from unprocessed dict
            for k in list(set(keys_to_pop)):
                self.unprocessed[direc].pop(k, None)

        if direc == 'forward':  # forward
            idx = 0
            self.min_res[0] = max(self.min_res[0], min(
                self.Label[direc].res[0], self.max_res[0]))
        else:
            idx = 1
            self.max_res[0] = min(self.max_res[0], max(
                self.Label[direc].res[0], self.min_res[0]))
        edges = [e for e in self.G.edges(data=True)
                 if e[idx] == self.Label[direc].node]
        if self.Label[direc] not in self.unprocessed[direc]:
            self.unprocessed[direc][self.Label[direc]] = {}

        list(map(_propagate_label, edges))
        _get_next_label()

    ###############
    # TERMINATION #
    ###############
    def terminate(self, direc):
        if self.direc_in == "both":
            if (self.finalpath['forward'] and self.finalpath['backward'] and
                    (self.finalpath['forward'][-1] ==
                        self.finalpath['backward'][-1])):
                return True
        else:
            if (self.finalpath['forward'][-1] == "Sink" and
                    not self.unprocessed['forward']):
                return True
            elif (self.finalpath['backward'][-1] == "Source" and
                  not self.unprocessed['backward']):
                return True
            if not self.Label[self.direc_in] and not self.G.edges():
                return True

    def save_final_path(self, direc):
        if self.Label[direc]:
            self.finalpath[direc] = self.Label[direc].path

    #############
    # DOMINANCE #
    #############
    def check_dominance(self, direc):
        # For all labels, check if it is dominated, or itself dominates other
        # labels. If this is found to be the case, the dominated label is
        # removed.
        for sub_dict in ({k: v} for k, v in self.unprocessed[direc].items()):
            k = list(sub_dict.keys())[0]  # call dict_keys object as a list
            for label in [key for v in sub_dict.values() for key in v.keys()]:
                if label.node == self.Label[direc].node:
                    if self.Label[direc].dominates(label, direc):
                        self.unprocessed[direc][k].pop(
                            label, None)
                        self.unprocessed[direc].pop(label, None)
                    elif label.dominates(self.Label[direc], direc):
                        self.unprocessed[direc][k].pop(self.Label[direc], None)
                        self.unprocessed[direc].pop(self.Label[direc], None)

    #################
    # PATH CHECKING #
    #################
    def join_paths(self):
        # check if paths are eligible to be joined. Joining phase as presented
        # in [2]

        if self.direc_in == 'both':
            if self.finalpath['forward'] and self.finalpath['backward']:
                # reverse order for backward path
                self.finalpath['backward'].reverse()
                return list(OrderedDict.fromkeys(
                    self.finalpath['forward'] + self.finalpath['backward']))
            elif self.finalpath['forward'] and not self.finalpath['backward']:
                return self.finalpath['forward']
            elif not self.finalpath['forward'] and self.finalpath['backward']:
                self.finalpath['backward'].reverse()
                return self.finalpath['backward']
        else:
            if self.direc_in == 'backward':
                self.finalpath[self.direc_in].reverse()
            return self.finalpath[self.direc_in]

    ###########################
    # Classify Algorithm Type #
    ###########################
    def name_algorithm(self):
        if self.HF == self.HB > self.U or self.direc_in == 'forward':
            logging.info('Monodirectional forward labeling algorithm')
        elif self.L < self.HF == self.HB < self.U:
            logging.info(
                'Bidirectional labeling algorithm with static halfway point')
        elif self.HF == self.HB < self.L or self.direc_in == 'backward':
            logging.info('Monodirectional backward labeling algorithm')
        elif self.U == self.HF > self.HB == self.L:
            logging.info('Bidirectional labeling algorithm with dynamic' +
                         ' halfway point.')
