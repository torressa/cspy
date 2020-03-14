from __future__ import absolute_import

from itertools import repeat
from operator import add, sub
from logging import getLogger
from collections import OrderedDict, deque

from numpy import zeros
from numpy.random import RandomState

# Local module imports
from cspy.checking import check
from cspy.algorithms.label import Label
from cspy.preprocessing import preprocess_graph

log = getLogger(__name__)


class BiDirectional:
    """
    Implementation of the bidirectional labeling algorithm with dynamic
    half-way point (`Tilk 2017`_). 
    This requires the half-way procedure from `Righini and Salani (2006)`_,
    also implemented.
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
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
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
        check(G, max_res, min_res, REF_forward, REF_backward, direction,
              __name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess,
                                  REF_backward)
        self.direc_in = direction
        self.max_res, self.min_res = max_res.copy(), min_res.copy()
        self.max_res_in, self.min_res_in = max_res.copy(), min_res.copy()
        # To expose results
        self.best_label = None
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
        else:
            Label._REF_forward = add
            Label._REF_backward = sub
        # Init with seed if given
        if seed is None:
            self.random_state = RandomState()
        elif isinstance(seed, int):
            self.random_state = RandomState(seed)
        elif isinstance(seed, RandomState):
            self.random_state = seed
        else:
            raise Exception("{} cannot be used to seed".format(seed))

    def run(self):
        """
        Calculate shortest path with resource constraints.
        """
        while self.currentLabel["forward"] or self.currentLabel["backward"]:
            direc = self._get_direction()
            if direc:
                self._algorithm(direc)
                self._check_dominance(direc)
            else:
                break
        return self._process_paths()

    # Return

    @property
    def path(self):
        """
        Get list with nodes in calculated path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.path

    @property
    def total_cost(self):
        """
        Get accumulated cost along the path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.weight

    @property
    def consumed_resources(self):
        """
        Get accumulated resources consumed along the path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.res

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
            if (self.currentLabel["forward"]
                    and not self.currentLabel["backward"]):
                return "forward"
            elif (not self.currentLabel["forward"]
                  and self.currentLabel["backward"]):
                return "backward"
            elif (self.currentLabel["forward"]
                  and self.currentLabel["backward"]):
                return self.random_state.choice(["forward", "backward"])
            else:  # if both are empty
                return
        else:
            if (not self.currentLabel["forward"]
                    and not self.currentLabel["backward"]):
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
        # If next label already been processed get another one.
        if next_label in self.processedLabels[direc]:
            next_label = self._get_next_label(direc, next_label)
        # Update current label
        self.currentLabel[direc] = next_label
        log.debug("current label = {}".format(next_label))

    def _propagate_label(self, edge, direc):
        # Label propagation #
        # Get new label from current Label
        new_label = self.currentLabel[direc].get_new_label(edge, direc)
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
                           if (lab not in self.processedLabels[direc]
                               and lab != exclude_label))
            return min(_labels, key=lambda x: x.weight)
        except ValueError:
            # No more keys to be processed under current label
            self.processedLabels[direc].append(self.currentLabel[direc])
            _labels = list(lab for lab in self.unprocessedLabels[direc].keys()
                           if (lab not in self.processedLabels[direc]
                               and lab != exclude_label))
            if _labels:
                return min(_labels, key=lambda x: x.weight)
            else:
                return None
        except KeyError:
            # No more keys to be processed.
            return None

    def _save_current_best_label(self, direc):
        current_label = self.currentLabel[direc]
        final_label = self.finalLabel[direc]
        try:
            current_label_dominates = current_label.dominates(
                final_label, direc)
            final_label_dominates = final_label.dominates(current_label, direc)
            # Current label dominates final
            if current_label_dominates:
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.finalLabel[direc] = current_label
            # Both non-dominated labels in this direction.
            elif (not current_label_dominates and not final_label_dominates):
                # flip directions
                flip_direc = "forward" if direc == "backward" else "backward"
                current_label_dominates_flipped = current_label.dominates(
                    final_label, flip_direc)
                if current_label_dominates_flipped:
                    self.finalLabel[direc] = current_label
        except Exception:
            # Labels are not comparable i.e. Belong to different nodes
            if (direc == "forward" and (current_label.path[-1] == "Sink"
                                        or final_label.node == "Source")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, self.currentLabel[direc].path))
                self.finalLabel[direc] = current_label
            elif (direc == "backward" and (current_label.path[-1] == "Source"
                                           or final_label.node == "Sink")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.finalLabel[direc] = current_label

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
            all_labels = deque(lab
                               for lab in self.unprocessedLabels[direc].keys()
                               if lab.node == self.currentLabel[direc].node
                               and lab != self.currentLabel[direc])
            all_labels.extend(
                lab for k, v in self.unprocessedLabels[direc].items()
                for lab in v if lab.node == self.currentLabel[direc].node
                and lab != self.currentLabel[direc])
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
            for k, sub_dict in self.unprocessedLabels[direc].items():
                if key_to_pop in sub_dict:
                    _idx = sub_dict.index(key_to_pop)
                    log.debug(
                        "Key {} removed from sub_dict".format(key_to_pop))
                    del self.unprocessedLabels[direc][k][_idx]

    ###################
    # PATH PROCESSING #
    ###################
    def _process_paths(self):
        # Processing of output path.
        if self.direc_in == "both":
            # If bi-directional algorithm used, run halfway procedure.
            return self._check_paths()
        else:
            # If mono-directional algorithm used, return the appropriate path
            if self.direc_in == "forward":
                self.best_label = self.finalLabel["forward"]
            else:
                self.best_label = self._process_final_bwd_label()

    def _check_paths(self):
        # if only forward path is source - sink
        if (self.finalLabel["forward"].path[-1] == "Sink"
                and self.finalLabel["backward"].path[0] != "Source"):
            self.best_label = self.finalLabel["forward"]
        # if only backward path is source - sink
        elif (self.finalLabel["backward"].path[-1] == "Source"
              and self.finalLabel["forward"].path[-1] != "Sink"):
            self.best_label = self._process_final_bwd_label()
        # if both paths are source - sink
        elif (self.finalLabel["backward"].path[-1] == "Source"
              and self.finalLabel["forward"].path[-1] == "Sink"):
            # if forward path has a lower weight
            if (self.finalLabel["forward"].weight <
                    self.finalLabel["backward"].weight):
                self.best_label = self.finalLabel["forward"]
            # if backward path has a lower weight
            elif (self.finalLabel["backward"].weight <
                  self.finalLabel["forward"].weight):
                self.best_label = self._process_final_bwd_label()
            # Otherwise (equal weight) save forward path
            else:
                self.best_label = self.finalLabel["forward"]
        # if combination of the two is required
        else:
            return self._half_way()

    def _process_final_bwd_label(self):
        # Reverse backward path
        label = self.finalLabel["backward"]
        label.path.reverse()
        label.res = self._invert_bwd_res(label)
        return label

    def _half_way(self):
        """
        Half-way procedure from `Righini and Salani (2006)`_.

        :return: list with the final path.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417

        """
        # Rename best forward and backward labels.
        fwd_best = self.finalLabel["forward"]
        bwd_best = self.finalLabel["backward"]
        # Get nodes associated with forward labels (to join with bwd_best)
        fwd_nodes = deque(self.G.predecessors(self.finalLabel["forward"].node))
        # Get nodes associated with backward labels (to join with fwd_best)
        bwd_nodes = deque(self.G.successors(self.finalLabel["forward"].node))
        # Get forward label with minimum "phi" w.r.t bwd_best
        # phi = difference in the mono resource
        fwd_min = min(list(lab for lab in self.unprocessedLabels["forward"]
                           if lab.node in fwd_nodes),
                      key=lambda x: abs(x.res[0] - bwd_best.res[0]))
        # Record the value of phi for
        phi_fwd_bwd = abs(fwd_min.res[0] - bwd_best.res[0])
        # Get backward label with minimum "phi" w.r.t fwd_best
        bwd_min = min(list(lab for lab in self.unprocessedLabels["backward"]
                           if lab.node in bwd_nodes),
                      key=lambda x: abs(fwd_best.res[0] - x.res[0]))
        phi_bwd_fwd = abs(fwd_best.res[0] - bwd_min.res[0])

        log.debug("{} with phi = {}".format(bwd_min, phi_bwd_fwd))

        if phi_fwd_bwd == phi_bwd_fwd:
            return (self._join_labels(fwd_min, bwd_best)
                    if fwd_min.res[0] > bwd_best.res[0] else self._join_labels(
                        fwd_best, bwd_min))
        else:
            return (self._join_labels(fwd_min, self.finalLabel["backward"])
                    if phi_fwd_bwd < phi_bwd_fwd else self._join_labels(
                        fwd_best, bwd_min))

    def _join_labels(self, fwd_label, bwd_label):
        """
        Join labels produced by a backward and forward label.

        Paramaters
        ----------
        fwd_label : label.Label object
        bwd_label : label.Label object
        """
        # reverse backward path
        bwd_label.path.reverse()
        # Reconstruct edge with edge data
        edge = (fwd_label.node, bwd_label.node,
                self.G[fwd_label.node][bwd_label.node])
        # Extend forward label along joining edge
        label = fwd_label.get_new_label(edge, "forward")
        # Get total consumed resources (inverted)
        total_res_bwd = self._invert_bwd_res(bwd_label)
        # Record total weight, total_res and final path
        weight = fwd_label.weight + edge[2]['weight'] + bwd_label.weight
        total_res = label.res + total_res_bwd
        final_path = fwd_label.path + bwd_label.path
        best_label = Label(weight, "Sink", total_res, final_path)
        # Check resource feasibility
        if best_label.feasibility_check(self.max_res_in, self.min_res_in):
            self.best_label = best_label
        else:
            raise Exception("Final path not resource feasible!")

    def _invert_bwd_res(self, label_to_invert):
        """
        Invert total backward resource to make it forward compatible.
        In the case when no REFs are provided, then this is simply the
        difference between the input maximum resource limit and the resources
        consumed by the backward path.
        However, if custom REFs are provided we have to ensure we apply it to
        obtain the inversion.

        Parameters
        ----------
        label_to_invert : label.Label object

        Returns
        -------
        array with forward compatible total resources consumed
        """
        if Label._REF_backward == sub:
            return self.max_res_in - label_to_invert.res
        # Otherwise:
        # Create dummy edge with 'res_cost' attribute of the input label
        edge = (0, 0, {'weight': 0, 'res_cost': label_to_invert.res})
        # Create dummy label with maximum resource
        label = Label(0, label_to_invert.node, self.max_res_in, [])
        # Extend the dummy along the dummy edge to apply the custom REF
        label_inverted = label.get_new_label(edge, "backward")
        return label_inverted.res