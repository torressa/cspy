from __future__ import absolute_import

from itertools import repeat
from logging import getLogger
from collections import OrderedDict, deque

from numpy import zeros
from numpy.random import RandomState

# Local module imports
from cspy.algorithms.label import Label
from cspy.preprocessing import check_and_preprocess

log = getLogger(__name__)


class BiDirectional:
    """
    Implementation of the bidirectional labeling algorithm with dynamic
    half-way point (`Tilk 2017`_).
    Depending on the range of values for U, L, we get
    four different algorithms. See self.name_algorithm and Notes.

    Parameters
    ----------
    G : object instance :class:`nx.Digraph()`
        must have ``n_res`` graph attribute and all edges must have
        ``res_cost`` attribute.

    max_res : list of floats
        :math:`[H_F, M_1, M_2, ..., M_{n\_res}]` upper bounds for resource
        usage (including initial forward stopping point).
        We must have ``len(max_res)`` :math:`\geq 2`.

    min_res : list of floats
        :math:`[H_B, L_1, L_2, ..., L_{n\_res}]` lower bounds for resource
        usage (including initial backward stopping point).
        We must have ``len(min_res)`` :math:`=` ``len(max_res)`` :math:`\geq 2`

    REF_forward REF_backward : function, optional
        Custom resource extension function. See `REFs`_ for more details.
        Default : additive, subtractive.

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    direction : string, optional
        preferred search direction.
        Either "both", "forward", or, "backward". Default : "both".

    seed : None or int or numpy.random.RandomState instance, optional
        seed for PSOLGENT class. Default : None (which gives a single value
        numpy.random.RandomState).

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs

    Returns
    -------
    list
        nodes in shortest path obtained.

    Notes
    -----
    The input graph must have a ``n_res`` attribute which must be
    :math:`\geq 2`. The edges in the graph must all have a ``res_cost``
    attribute.

    According to the inputs, four different algorithms can be used.
    If you'd like to check which algorithm is running given the resource
    limits, call the method :func:`BiDirectional.name_algorithm()`
    for a log with the classification.

    - ``direction`` = "forward": Monodirectional forward labeling algorithm
    - :math:`H_F == H_B`: Bidirectional labeling algorithm with static halfway point.
    - ``direction`` = "backward": Monodirectional backward labeling algorithm
    - :math:`H_F > H_B`: Bidirectional labeling algorithm with dynamic halfway point.
    - :math:`H_F < H_B`: The algorithm won't go anywhere!

    Example
    -------
    To run the algorithm, create a :class:`BiDirectional` instance and call
    ``run``.

    .. code-block:: python

        >>> from cspy import BiDirectional
        >>> from networkx import DiGraph
        >>> from numpy import array
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
        >>> G.add_edge("A", "B", res_cost=array([1, 0.3]), weight=0)
        >>> G.add_edge("A", "C", res_cost=array([1, 0.1]), weight=0)
        >>> G.add_edge("B", "C", res_cost=array([1, 3]), weight=-10)
        >>> G.add_edge("B", "Sink", res_cost=array([1, 2]), weight=10)
        >>> G.add_edge("C", "Sink", res_cost=array([1, 10]), weight=0)
        >>> max_res, min_res = [4, 20], [1, 0]
        >>> path = BiDirectional(G, max_res, min_res, direction="both").run()
        >>> print(path)
        ["Source", "A", "B", "C", "Sink"]

    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    """

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 REF_forward=None,
                 REF_backward=None,
                 preprocess=False,
                 direction="both",
                 seed=None):
        # Check inputs and preprocess G unless option disabled
        self.G = check_and_preprocess(preprocess, G, max_res, min_res,
                                      REF_forward, REF_backward, direction,
                                      __name__)
        self.direc_in = direction
        self.max_res, self.min_res = max_res.copy(), min_res.copy()
        # Algorithm specific parameters #
        # Current forward and backward labels
        self.currentLabel = OrderedDict({
            "forward":
            Label(0, "Source", zeros(G.graph["n_res"]), ["Source"]),
            "backward":
            Label(0, "Sink", max_res, ["Sink"])
        })
        # Unprocessed labels dict (both directions)
        self.unprocessedLabels = OrderedDict({
            "forward": OrderedDict({}),
            "backward": OrderedDict({})
        })
        # Processed labels dict
        self.processedLabels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # Final labels dict.
        self.finalLabel = OrderedDict({
            "forward": self.currentLabel["forward"],
            "backward": self.currentLabel["backward"]
        })

        # If given, set REFs for dominance relations and feasibility checks
        if REF_forward and REF_backward:
            Label._REF_forward = REF_forward
            Label._REF_backward = REF_backward
        # Init with seed if given
        if seed is None:
            self.random_state = RandomState()
        elif isinstance(seed, int):
            self.random_state = RandomState(seed)
        elif isinstance(seed, RandomState):
            self.random_state = seed
        else:
            raise Exception(
                '{} cannot be used to seed numpy.random.RandomState'.format(
                    seed))

    def run(self):
        while self.currentLabel["forward"] or self.currentLabel["backward"]:
            direc = self._get_direction()
            if direc:
                self._algorithm(direc)
                self._check_dominance(direc)
            elif not direc or self._terminate(direc):
                break
        # Otherwise return either path
        return self._join_paths()

    ###########################
    # Classify Algorithm Type #
    ###########################
    def name_algorithm(self):
        """
        Determine which algorithm is running.
        """
        HF, HB = self.max_res[0], self.min_res[0]
        if self.direc_in == "forward":
            log.info("Monodirectional forward labeling algorithm")
        elif self.direc_in == "backward":
            log.info("Monodirectional backward labeling algorithm")
        elif HF > HB:
            log.info("Bidirectional labeling algorithm with" +
                     " dynamic halfway point")
        else:
            log.info("The algorithm can't move in either direction!")

    #############
    # DIRECTION #
    #############
    def _get_direction(self):
        if self.direc_in == "both":
            if (self.currentLabel["forward"] and
                    not self.currentLabel["backward"]):
                return "forward"
            elif (not self.currentLabel["forward"] and
                  self.currentLabel["backward"]):
                return "backward"
            elif (self.currentLabel["forward"] and
                  self.currentLabel["backward"]):
                return self.random_state.choice(["forward", "backward"])
            else:  # if both are empty
                return
        else:
            if (not self.currentLabel["forward"] and
                    not self.currentLabel["backward"]):
                return
            elif not self.currentLabel[self.direc_in]:
                return
            else:
                return self.direc_in

    #############
    # ALGORITHM #
    #############
    def _algorithm(self, direc):
        if direc == "forward":  # forward
            idx = 0  # index for head node
            # Update backwards half-way point
            self.min_res[0] = max(
                self.min_res[0],
                min(self.currentLabel[direc].res[0], self.max_res[0]))
        else:  # backward
            idx = 1  # index for tail node
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0],
                max(self.currentLabel[direc].res[0], self.min_res[0]))
        # Select edges with the same head/tail node as the current label node.
        edges = deque(e for e in self.G.edges(data=True)
                      if e[idx] == self.currentLabel[direc].node)
        # If Label not been seen before, initialise a list
        if (self.currentLabel[direc] not in self.unprocessedLabels[direc] and
                self.currentLabel[direc] not in self.processedLabels[direc]):
            self.unprocessedLabels[direc][self.currentLabel[direc]] = deque()
        # Propagate current label along all suitable edges in current direction
        list(map(self._propagate_label, edges, repeat(direc, len(edges))))
        # Extend label
        next_label = self._get_next_label(direc)
        if next_label in self.processedLabels[direc]:
            next_label = self._get_next_label(direc, next_label)
        # Update current label
        self.currentLabel[direc] = next_label

    def _propagate_label(self, edge, direc):
        # Label propagation #
        weight, res_cost = edge[2]["weight"], edge[2]["res_cost"]
        # Get new label from current Label
        new_label = self.currentLabel[direc].get_new_label(
            edge, direc, weight, res_cost)
        if new_label and new_label.feasibility_check(self.max_res,
                                                     self.min_res):
            # If label doesn't exist and is resource feasible
            self.unprocessedLabels[direc][self.currentLabel[direc]].append(
                new_label)

    def _get_next_label(self, direc, exclude_label=None):
        # Label Extension #
        try:
            # Try to get labels create from the current one.
            _labels = list(lab for lab in self.unprocessedLabels[direc][
                self.currentLabel[direc]]
                           if (lab not in self.processedLabels[direc] and
                               lab != exclude_label))
            return min(_labels, key=lambda x: x.weight)
        except ValueError:
            # No more keys to be processed under current label
            self.processedLabels[direc].append(self.currentLabel[direc])
            _labels = list(lab for lab in self.unprocessedLabels[direc].keys()
                           if (lab not in self.processedLabels[direc] and
                               lab != exclude_label))
            if _labels:
                return min(_labels, key=lambda x: x.weight)
            else:
                return None
        except KeyError:
            # No more keys to be processed.
            return None

    def _save_current_best_label(self, direc):
        try:
            if self.currentLabel[direc].dominates(self.finalLabel[direc],
                                                  direc):
                log.debug("Saving {} as best, with path {}".format(
                    self.currentLabel[direc], self.currentLabel[direc].path))
                self.finalLabel[direc] = self.currentLabel[direc]
        except Exception:
            # Labels are not comparable
            if (direc == "forward" and
                ((self.currentLabel[direc].path[-1] == "Sink" or
                  self.finalLabel[direc].node == "Source") or
                 ((self.currentLabel[direc].node not in
                   self.finalLabel[direc].path) and
                  (self.currentLabel[direc].weight <=
                   self.finalLabel[direc].weight)))):
                log.debug("Saving {} as best, with path {}".format(
                    self.currentLabel[direc], self.currentLabel[direc].path))
                self.finalLabel[direc] = self.currentLabel[direc]
            elif (direc == "backward" and
                  ((self.currentLabel[direc].path[-1] == "Source" or
                    self.finalLabel[direc].node == "Sink") or
                   ((self.currentLabel[direc].node not in
                     self.finalLabel[direc].path) and
                    (self.currentLabel[direc].weight <=
                     self.finalLabel[direc].weight)))):
                log.debug("Saving {} as best, with path {}".format(
                    self.currentLabel[direc], self.currentLabel[direc].path))
                self.finalLabel[direc] = self.currentLabel[direc]

    #############
    # DOMINANCE #
    #############
    def _check_dominance(self, direc):
        """
        For all labels, check if it is dominated, or itself dominates other
        labels. If this is found to be the case, the dominated label is
        removed.
        """
        if self.currentLabel[direc]:
            keys_to_pop = deque()
            all_labels = deque(
                lab for lab in self.unprocessedLabels[direc].keys()
                if lab.node == self.currentLabel[direc].node and
                lab != self.currentLabel[direc])
            all_labels.extend(
                lab for k, v in self.unprocessedLabels[direc].items()
                for lab in v if lab.node == self.currentLabel[direc].node and
                lab != self.currentLabel[direc])
            keys_to_pop.extend(
                lab for lab in all_labels
                if self.currentLabel[direc].dominates(lab, direc))
            keys_to_pop.extend([
                lab for lab in self.processedLabels[direc]
                if lab != self.finalLabel[direc]
            ])

            if any(
                    lab.dominates(self.currentLabel[direc], direc)
                    for lab in all_labels):
                keys_to_pop.append(self.currentLabel[direc])
            else:
                self._save_current_best_label(direc)
            self._remove_unprocessed_labels(keys_to_pop, direc)

    def _remove_unprocessed_labels(self, keys_to_pop, direc):
        # Remove all processed labels from unprocessed dict
        for key_to_pop in list(set(keys_to_pop)):
            if key_to_pop in self.unprocessedLabels[direc]:
                log.debug("Key {} removed".format(key_to_pop))
                del self.unprocessedLabels[direc][key_to_pop]
            for k, sub_dict in self.unprocessedLabels[direc].items():
                if key_to_pop in sub_dict:
                    _idx = sub_dict.index(key_to_pop)
                    log.debug("Key {} removed from sub_dict".format(key_to_pop))
                    del self.unprocessedLabels[direc][k][_idx]

    ###############
    # TERMINATION #
    ###############
    def _terminate(self, direc):
        if self.direc_in == "both":
            if (not self.unprocessedLabels["forward"] or
                    not self.unprocessedLabels["backward"]):
                return True
        else:
            if (self.direc_in == "forward" and
                    self.finalLabel["forward"].path[-1] == "Sink" and
                    not self.unprocessedLabels["forward"]):
                return True
            elif (self.direc_in == "backward" and
                  self.finalLabel["backward"].path[-1] == "Source" and
                  not self.unprocessedLabels["backward"]):
                return True

    #################
    # PATH CHECKING #
    #################
    def _join_paths(self):
        # check if paths are eligible to be joined
        if self.direc_in == "both":
            return self._check_paths()
        else:
            if self.direc_in == "backward":
                self.finalLabel[self.direc_in].path.reverse()
            return self.finalLabel[self.direc_in].path

    def _check_paths(self):
        # Reverse backward path
        self.finalLabel["backward"].path.reverse()
        if (self.finalLabel["forward"].path[-1] == "Sink" and
                self.finalLabel["backward"].path[0] != "Source"):
            # if only forward path
            return self.finalLabel["forward"].path
        elif (self.finalLabel["backward"].path[0] == "Source" and
              self.finalLabel["forward"].path[-1] != "Sink"):
            # if only backward path
            return self.finalLabel["backward"].path
        elif (self.finalLabel["backward"].path[0] == "Source" and
              self.finalLabel["forward"].path[-1] == "Sink"):
            # if both paths
            if self.finalLabel["forward"].weight < self.finalLabel[
                    "backward"].weight:
                # if forward path has a lower weight
                return self.finalLabel["forward"].path
            elif self.finalLabel["backward"].weight < self.finalLabel[
                    "forward"].weight:
                # if backward path has a lower weight
                return self.finalLabel["backward"].path
            else:
                # Otherwise (equal weight) return either path
                return (self.finalLabel["forward"].path
                        if self.random_state.random_sample() < 0.5 else
                        self.finalLabel["backward"].path)
        else:
            # if combination of the two is required
            return list(
                OrderedDict.fromkeys(self.finalLabel["forward"].path +
                                     self.finalLabel["backward"].path))
