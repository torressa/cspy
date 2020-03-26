from __future__ import absolute_import

from copy import deepcopy
from itertools import repeat
from operator import add, sub
from logging import getLogger
from collections import OrderedDict, deque

from numpy import zeros, array
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
        >>> bidirec = BiDirectional(G, max_res, min_res, direction="both")
        >>> bidirec.run()
        >>> print(bidirec.path)
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
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        # To expose results
        self.best_label = None

        # Algorithm specific parameters #
        # Current forward and backward labels
        self.current_label = OrderedDict({
            "forward":
            Label(0, "Source", zeros(G.graph["n_res"]), ["Source"]),
            "backward":
            Label(0, "Sink", max_res, ["Sink"])
        })
        # Unprocessed labels dict (both directions)
        self.unprocessed_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # Processed labels dict
        self.processed_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # Final labels dicts for unidirectional search
        self.final_label = None

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
        while self.current_label["forward"] or self.current_label["backward"]:
            direc = self._get_direction()
            if direc:
                self._algorithm(direc)
                self._check_dominance(direc)
            else:
                break
        return self._process_paths()

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
            if (self.current_label["forward"]
                    and not self.current_label["backward"]):
                return "forward"
            elif (not self.current_label["forward"]
                  and self.current_label["backward"]):
                return "backward"
            elif (self.current_label["forward"]
                  and self.current_label["backward"]):
                return self.random_state.choice(["forward", "backward"])
            else:  # if both are empty
                return
        else:
            if (not self.current_label["forward"]
                    and not self.current_label["backward"]):
                return
            elif not self.current_label[self.direc_in]:
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
                min(self.current_label[direc].res[0], self.max_res[0]))
        else:  # backward
            idx = 1  # index for tail node
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0],
                max(self.current_label[direc].res[0], self.min_res[0]))
        # Select edges with the same head/tail node as the current label node.
        edges = deque(e for e in self.G.edges(data=True)
                      if e[idx] == self.current_label[direc].node)
        # If Label not been seen before, initialise a list
        # Propagate current label along all suitable edges in current direction
        list(map(self._propagate_label, edges, repeat(direc, len(edges))))
        # Extend label
        next_label = self._get_next_label(direc)
        # Update current label
        self.current_label[direc] = next_label

    def _propagate_label(self, edge, direc):
        # Label propagation #
        # Get new label from current Label
        new_label = self.current_label[direc].get_new_label(edge, direc)
        # If the new label is resource feasible
        if new_label and new_label.feasibility_check(self.max_res,
                                                     self.min_res):
            # And is not already in the unprocessed labels list
            if (new_label not in self.unprocessed_labels[direc]
                    and new_label not in self.processed_labels[direc]):
                self.unprocessed_labels[direc].append(new_label)

    def _get_next_label(self, direc, exclude_label=None):
        # Label Extension #
        # Add current label to processed list.
        current_label = self.current_label[direc]
        unproc_labels = self.unprocessed_labels[direc]
        self.processed_labels[direc].append(current_label)
        self._remove_unprocessed_labels([current_label], direc)
        # Return label with minimum monotone resource for the forward search
        # and the maximum monotone resource for the backward search
        if unproc_labels:
            if direc == "forward":
                return min(unproc_labels, key=lambda x: x.res[0])
            else:
                return max(unproc_labels, key=lambda x: x.res[0])
        else:
            return None

    #############
    # DOMINANCE #
    #############
    def _check_dominance(self, direc):
        """
        For all labels, check if it is dominated, or itself dominates other
        labels. If this is found to be the case, the dominated label is
        removed.
        """
        # Reference attributes
        current_label = self.current_label[direc]
        unproc_labels = self.unprocessed_labels[direc]
        # If current label is not None (at termination)
        if current_label:
            keys_to_pop = deque()
            # Gather all comparable labels (same node)
            all_labels = deque(
                lab for lab in unproc_labels
                if lab.node == current_label.node and lab != current_label)
            # Add to list for removal if they are dominated
            keys_to_pop.extend(lab for lab in all_labels
                               if current_label.dominates(lab, direc))
            # Add current label for removal if itself is dominated
            if any(lab.dominates(current_label, direc) for lab in all_labels):
                keys_to_pop.append(current_label)
            # If not bidirectional algorithm, check and save current label
            elif self.direc_in != "both":
                self._save_current_best_label(direc)
            self._remove_unprocessed_labels(keys_to_pop, direc)

    def _remove_unprocessed_labels(self, keys_to_pop, direc):
        # Remove all processed labels from unprocessed dict
        for key_to_pop in list(set(keys_to_pop)):
            if key_to_pop in self.unprocessed_labels[direc]:
                idx = self.unprocessed_labels[direc].index(key_to_pop)
                del self.unprocessed_labels[direc][idx]

    def _save_current_best_label(self, direc):
        """
        Label saving for unidirectional searches
        """
        current_label = self.current_label[direc]
        final_label = self.final_label
        # If first label
        if not final_label:
            self.final_label = current_label
            return
        try:
            if self._full_dominance_check(current_label, final_label, direc):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label
        except Exception:
            # Labels are not comparable i.e. Belong to different nodes
            if (direc == "forward" and (current_label.path[-1] == "Sink"
                                        or final_label.node == "Source")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label
            elif (direc == "backward" and (current_label.path[-1] == "Source"
                                           or final_label.node == "Sink")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label

    @staticmethod
    def _full_dominance_check(label1, label2, direc):
        """
        Checks whether label 1 dominates label 2 for the input direction.
        In the case when both labels are non-dominated,
        the direction is flipped labels are compared again.
        """
        label1_dominates = label1.dominates(label2, direc)
        label2_dominates = label2.dominates(label1, direc)
        # label1 dominates label2 for the input direction
        if label1_dominates:
            return True
        # Both non-dominated labels in this direction.
        elif (not label1_dominates and not label2_dominates):
            # flip directions
            flip_direc = "forward" if direc == "backward" else "backward"
            label1_dominates_flipped = label1.dominates(label2, flip_direc)
            # label 1 dominates label2 in the flipped direction
            if label1_dominates_flipped:
                return True

    ###################
    # PATH PROCESSING #
    ###################
    def _process_paths(self):
        # Processing of output path.
        if self.direc_in == "both":
            # If bi-directional algorithm used, run path joining procedure.
            self._join_paths()
        else:
            # If mono-directional algorithm used, return the appropriate path
            if self.direc_in == "forward":
                self.best_label = self.final_label
            else:
                self.best_label = self._process_bwd_label(self.final_label)

    def _process_bwd_label(self, label):
        # Reverse backward path and inverts resource consumption
        label.path.reverse()
        label.res = self._invert_bwd_res(label)
        return label

    def _join_paths(self):
        """
        The procedure "Join" or Algorithm 3 from `Righini and Salani (2006)`_.

        :return: list with the final path.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
        """
        halfway = (self.max_res[0] - self.min_res[0]) / 2
        # Parameter required for the Half-way procedure
        difference = 1  # difference in the monotone resource of any pair of labels
        for i in self.G.nodes():
            for fwd_label in (l for l in self.processed_labels["forward"]
                              if l.node == i and l.res[0] > halfway):
                for j in self.G.nodes():
                    bwd_labels_sorted = sorted(deque(
                        l for l in self.processed_labels["backward"]
                        if l.node == j),
                                               key=lambda x: x.weight)
                    for bwd_label in bwd_labels_sorted:
                        # Merge two labels
                        merged_label = self._merge_labels(fwd_label, bwd_label)
                        if ((self.best_label and merged_label) and
                                merged_label.weight > self.best_label.weight):
                            break
                        # Check resource feasibility
                        if (merged_label and merged_label.feasibility_check(
                                self.max_res_in, self.min_res_in)
                                and self._half_way(fwd_label, bwd_label,
                                                   difference)):
                            # Save label
                            self._save(merged_label)

    @staticmethod
    def _half_way(fwd_label, bwd_label, difference):
        """
        Half-way check from `Righini and Salani (2006)`_.
        Checks if a pair of labels is closest to the half-way point.

        :return: bool. True if the half-way check passes, false otherwise.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417

        """
        _difference = fwd_label.res[0] - bwd_label.res[0]
        if difference > 0 and _difference < 0:
            return True
        else:
            difference = _difference
            return False

    def _merge_labels(self, fwd_label, bwd_label):
        """
        Merge labels produced by a backward and forward label.

        Paramaters
        ----------
        fwd_label : label.Label object
        bwd_label : label.Label object

        Returns
        -------
        merged_label : label.Label object
            If an s-t compatible path can be obtained the appropriately
            extended and merged label is returned

        None
            Otherwise.
        """
        # Make a copy of the backward label
        _bwd_label = deepcopy(bwd_label)
        # Process backward label
        self._process_bwd_label(_bwd_label)
        # Reconstruct edge with edge data
        try:
            edge = (fwd_label.node, _bwd_label.node,
                    self.G[fwd_label.node][_bwd_label.node])
            # Extend forward label along joining edge
            label = fwd_label.get_new_label(edge, "forward")
            if not label:
                return
        # Catch when an edge (fwd_label.node, _bwd_label.node) doesn't exist
        except KeyError:
            return
        # Get total consumed resources (inverted)
        total_res_bwd = _bwd_label.res
        # Record total weight, total_res and final path
        weight = fwd_label.weight + edge[2]['weight'] + _bwd_label.weight
        total_res = label.res + total_res_bwd
        final_path = fwd_label.path + _bwd_label.path
        merged_label = Label(weight, "Sink", total_res, final_path)
        return merged_label

    def _save(self, label):
        # Saves a label for exposure
        if not self.best_label or self._full_dominance_check(
                label, self.best_label, "forward"):
            self.best_label = label

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
