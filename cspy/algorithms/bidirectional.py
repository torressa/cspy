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
    """
    Implementation of the bidirectional labeling algorithm with dynamic
    half-way point Tilk2017.
    Depending on the range of values for self.HF = HF and self.HB = HB, we get
    four different algorithms. See self.name_algorithm.

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    max_res : list of floats
        :math:`[L, M_1, M_2, ..., M_{n\_res}]`
        upper bound for resource usage.
        We must have ``len(max_res)`` :math:`\geq 2`

    min_res : list of floats
        :math:`[U, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource usage.
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    direc_in : string, optional
        preferred search direction.
        Either 'both','forward', or, 'backward'. Default : 'both'.

    preprocess : bool, optional
        enables preprocessing routine.

    REF_forward REF_backward : functions, optional
        non-additive resource extension functions.

    Returns
    -------
    list
        nodes in shortest path obtained.

    Notes
    -----
    The input graph must have a ``n_res`` attribute in the input graph has
    to be :math:`\geq 2`. The edges in the graph must all have a ``res_cost``
    attribute.

    According to the inputs, four different algorithms can be implemented:

    - HF = HB > U or ``direc_in`` = 'forward': Monodirectional forward labeling algorithm
    - L < HF = HB < U: Bidirectional labeling algorithm with static halfway point
    - HF = HB < L or ``direc_in`` == 'backward': Monodirectional backward labeling algorithm
    - U = HF > HB = L: Bidirectional labeling algorithm with dynamic halfway point.

    Example
    -------
    To run the algorithm, create a :class:`BiDirectional` instance and call
    ``run``.

    .. code-block:: python

        >>> import cspy
        >>> import networkx as nx
        >>> G = nx.DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
        >>> G.add_edge('A', 'B', res_cost=[1, 0.3], weight=0)
        >>> G.add_edge('A', 'C', res_cost=[1, 0.1], weight=0)
        >>> G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
        >>> G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
        >>> G.add_edge('C', 'Sink', res_cost=[1, 10], weight=0)
        >>> max_res, min_res = [4, 20], [1, 0]
        >>> algObj = BiDirectional(G, max_res, min_res, direction='both')
        >>> path = algObj.run()
        >>> print(path)
        ['Source', 'A', 'B', 'C', 'Sink']

    """

    def __init__(self, G, max_res, min_res, direction='both',
                 preprocess=True, REF_forward=add, REF_backward=sub,):

        self.G = check_and_preprocess(
            preprocess, G, max_res, min_res, direction)
        self.direc_in = direction
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
        """ For all labels, check if it is dominated, or itself dominates other
        labels. If this is found to be the case, the dominated label is
        removed """
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
        # check if paths are eligible to be joined

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
                return _check_paths()
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
