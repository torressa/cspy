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
# hi
import random
import logging
from operator import add, sub
from collections import OrderedDict
from cspy.label import Label
from cspy.preprocessing import preprocess_graph, check_inputs


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
        G :: nx.Digraph() object with n_res attribute;
        max_res :: list of floats, [L, M_1, M_2, ..., M_nres]
                    upper bound for resource usage;
        min_res :: list of floats, [U, L_1, L_2, ..., L_nres]
                    lower bounds for resource usage.
    '''

    def __init__(self, G, max_res, min_res, direc_in='both', preprocess=True,
                 REF_forward=add, REF_backward=sub):

        check_inputs(max_res, min_res, direc_in)

        self.G, _ = preprocess_graph(
            G, max_res, min_res) if preprocess else (G, [])
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
            self.G.remove_edge(*edge[: 2])

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
                    break
                else:
                    keys_to_pop.extend([self.Label[direc], key])
            else:  # if no break
                self.save_final_path(direc)
                keys_to_pop.append(self.Label[direc])
                self.Label[direc] = None
            for k in keys_to_pop:
                self.unprocessed[direc].pop(k, None)

        if direc == 'forward':  # forward
            idx = 0
            self.min_res[0] = max(self.min_res[0], min(
                self.Label[direc].res[0], self.max_res[0]))
        else:
            idx = 1
            self.max_res[0] = min(self.max_res[0], max(
                self.Label[direc].res[0], self.min_res[0]))
        if not self.Label[direc].feasibility_check(
                self.max_res, self.min_res, direc):
            return
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
            elif not self.Label[self.direc_in] and not self.G.edges():
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
                if self.Label[direc].dominates(label):
                    self.unprocessed[direc][k].pop(
                        label, None)
                    self.unprocessed[direc].pop(label, None)
                elif label.dominates(self.Label[direc]):
                    self.unprocessed[direc][k].pop(label, None)
                    self.unprocessed[direc].pop(label, None)

    #################
    # PATH CHECKING #
    #################
    def join_paths(self):
        # check if paths are eligible to be joined. Joining phase as presented
        # in [2]
        def _check_paths():
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

        if self.direc_in == 'both':
            if self.finalpath['forward'] and self.finalpath['backward']:
                # reverse order for backward path
                self.finalpath['backward'].reverse()
                joined_path = _check_paths()
                logging.debug("[{0}] {1}".format(__name__, joined_path))
                return joined_path
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
        if self.HF == self.HB > self.U:
            logging.info('Monodirectional forward labeling algorithm')
        elif self.L < self.HF == self.HB < self.U:
            logging.info(
                'Bidirectional labeling algorithm with static halfway point')
        elif self.HF == self.HB < self.L:
            logging.info('Monodirectional backward labeling algorithm')
        elif self.U == self.HF > self.HB == self.L:
            logging.info('Bidirectional labeling algorithm with dynamic' +
                         ' halfway point.')
