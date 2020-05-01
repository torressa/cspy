from __future__ import absolute_import

from copy import deepcopy
from itertools import repeat
from operator import add, sub
from logging import getLogger
from collections import OrderedDict, deque

from numpy import array
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
    This requires the joining procedure (Algorithm 3) from
    `Righini and Salani (2006)`_, also implemented.
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

    preprocess : bool, optional
        enables preprocessing routine. Default : False.

    direction : string, optional
        preferred search direction.
        Either "both", "forward", or, "backward". Default : "both".

    method : string, optional
        preferred method for determining search direction.
        Either "random", "generated" (direction with least number of generated labels),
        "processed" (direction with least number of processed labels), or,
        "unprocessed" (direction with least number of unprocessed labels).
        Default: "random".

    seed : None or int or numpy.random.RandomState instance, optional
        seed for PSOLGENT class. Default : None (which gives a single value
        numpy.random.RandomState).

    REF_forward, REF_backward, REF_join : functions, optional
        Custom resource extension functions. See `REFs`_ for more details.
        Default : additive.

    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs
    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
    """

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 preprocess=False,
                 direction="both",
                 method="random",
                 seed=None,
                 REF_forward=None,
                 REF_backward=None,
                 REF_join=None):

        # Check inputs
        check(G,
              max_res,
              min_res,
              REF_forward=REF_forward,
              REF_backward=REF_backward,
              REF_join=REF_join,
              direction=direction,
              algorithm=__name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF_forward)
        self.REF_join = REF_join
        self.direc_in = direction
        self.max_res, self.min_res = max_res.copy(), min_res.copy()
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        self.method = method
        # To expose results
        self.best_label = None

        # Algorithm specific parameters #
        # set bounds for bacward search
        bwd_start = deepcopy(min_res)
        bwd_start[0] = max_res[0]
        # Current forward and backward labels
        self.current_label = OrderedDict({
            "forward": Label(0, "Source", min_res, ["Source"]),
            "backward": Label(0, "Sink", bwd_start, ["Sink"])
        })
        # Unprocessed labels dict (both directions)
        self.unprocessed_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # All generated label
        self.generated_labels = OrderedDict({"forward": 0, "backward": 0})
        # Best labels
        # (with initial labels for small cases, see:
        # https://github.com/torressa/cspy/issues/38 )
        self.best_labels = OrderedDict({
            "forward": deque([self.current_label["forward"]]),
            "backward": deque([self.current_label["backward"]])
        })
        # Final labels dicts for unidirectional search
        self.final_label = None

        # If given, set REFs for dominance relations and feasibility checks
        if REF_forward:
            Label._REF_forward = REF_forward
        else:
            Label._REF_forward = add
        if REF_backward:
            Label._REF_backward = REF_backward
        else:
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
        Logs algorithm classification at INFO level.
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
            if (self.current_label["forward"] and
                    not self.current_label["backward"]):
                return "forward"
            elif (not self.current_label["forward"] and
                  self.current_label["backward"]):
                return "backward"
            elif (self.current_label["forward"] and
                  self.current_label["backward"]):
                if self.method == "random":
                    # return a random direction
                    return self.random_state.choice(["forward", "backward"])
                elif self.method == "generated":
                    # return direction with least number of generated labels
                    return ("forward" if self.generated_labels["forward"] <
                            self.generated_labels["backward"] else "backward")
                elif self.method == "processed":
                    # return direction with least number of "processed" labels
                    return ("forward" if len(self.best_labels["forward"]) < len(
                        self.best_labels["backward"]) else "backward")
                elif self.method == "unprocessed":
                    # return direction with least number of unprocessed_labels labels
                    return ("forward" if len(self.unprocessed_labels["forward"])
                            < len(self.unprocessed_labels["backward"]) else
                            "backward")
            else:  # if both are empty
                return
        else:
            if (not self.current_label["forward"] and
                    not self.current_label["backward"]):
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
            idx = 0  # index for tail node
            # Update backwards half-way point
            self.min_res[0] = max(
                self.min_res[0],
                min(self.current_label[direc].res[0], self.max_res[0]))
        else:  # backward
            idx = 1  # index for head node
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0],
                max(self.current_label[direc].res[0], self.min_res[0]))
        # Select edges with the same tail/head node as the current label node.
        edges = deque(e for e in self.G.edges(data=True)
                      if e[idx] == self.current_label[direc].node)
        # Propagate current label along all suitable edges in current direction
        for edge in edges:
            self._propagate_label(edge, direc)
        # Extend label
        next_label = self._get_next_label(direc)
        self.current_label[direc] = next_label
        self._check_dominance(next_label, direc)

    def _propagate_label(self, edge, direc):
        new_label = self.current_label[direc].get_new_label(edge, direc)
        # If the new label is resource feasible
        if new_label and new_label.feasibility_check(self.max_res,
                                                     self.min_res):
            # And is not already in the unprocessed labels list
            if (new_label not in self.unprocessed_labels[direc]):
                self.unprocessed_labels[direc].append(new_label)

    def _get_next_label(self, direc):
        current_label = self.current_label[direc]
        unproc_labels = self.unprocessed_labels[direc]

        # Add 1 to count of generated_labels
        self.generated_labels[direc] += 1
        self._remove_labels([current_label], direc, unproc=True)
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
    def _check_dominance(self, label_to_check, direc, unproc=True, best=False):
        """
        For all labels, checks if ``label_to_check`` is dominated,
        or itself dominates any other label in either the unprocessed_labels
        list or the non-dominated labels list.
        If this is found to be the case, the dominated label(s) is(are)
        removed from the appropriate list.
        """
        # Select appropriate list to check
        if unproc:
            labels_to_check = self.unprocessed_labels[direc]
        elif best:
            labels_to_check = self.best_labels[direc]
        # If label is not None (at termination)
        if label_to_check:
            labels_to_pop = deque()
            # Gather all comparable labels (same node)
            all_labels = deque(
                l for l in labels_to_check
                if l.node == label_to_check.node and l != label_to_check)
            # Add to list for removal if they are dominated
            labels_to_pop.extend(
                l for l in all_labels if label_to_check.dominates(l, direc))
            # Add input label for removal if itself is dominated
            if any(l.dominates(label_to_check, direc) for l in all_labels):
                labels_to_pop.append(label_to_check)
            elif unproc:
                # check and save current label
                self._save_current_best_label(direc)
            # if unprocessed labels checked then remove labels_to_pop
            if unproc:
                self._remove_labels(labels_to_pop, direc, unproc, best)
            # Otherwise, return labels_to_pop for later removal
            elif best:
                return labels_to_pop

    def _remove_labels(self, labels_to_pop, direc, unproc=True, best=False):
        """
        Remove all labels in ``labels_to_pop`` from either the array of
        unprocessed labels or the array of non-dominated labels
        """
        # Remove all processed labels from unprocessed dict
        for label_to_pop in deque(set(labels_to_pop)):
            if unproc and label_to_pop in self.unprocessed_labels[direc]:
                idx = self.unprocessed_labels[direc].index(label_to_pop)
                del self.unprocessed_labels[direc][idx]
            elif best and label_to_pop in self.best_labels[direc]:
                idx = self.best_labels[direc].index(label_to_pop)
                del self.best_labels[direc][idx]

    def _save_current_best_label(self, direc):
        """
        Label saving
        """
        current_label = self.current_label[direc]
        final_label = self.final_label

        if self.direc_in == "both":
            self.best_labels[direc].append(current_label)
            flip_direc = "forward" if direc == "backward" else "backward"
            # Check if other direction traversed
            # (must contain more than just the initial label)
            # If it has, then we are done as labels will have to be joined
            if len(self.best_labels[flip_direc]) > 1:
                return
            # Otherwise save label as with the single direction case

        # Saving for single direction
        # If first label
        if not final_label:
            self.final_label = current_label
            return
        # Otherwise, check dominance and replace
        try:
            if self._full_dominance_check(current_label, final_label, direc):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label
        except Exception:
            # Labels are not comparable i.e. Belong to different nodes
            if (direc == "forward" and (current_label.path[-1] == "Sink" or
                                        final_label.node == "Source")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label
            elif (direc == "backward" and (current_label.path[-1] == "Source" or
                                           final_label.node == "Sink")):
                log.debug("Saving {} as best, with path {}".format(
                    current_label, current_label.path))
                self.final_label = current_label

    @staticmethod
    def _full_dominance_check(label1, label2, direc):
        """
        Checks whether label 1 dominates label 2 for the input direction.
        In the case when neither dominates , i.e. they are non-dominated,
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
            elif label1.weight < label2.weight:
                return True

    ###################
    # PATH PROCESSING #
    ###################
    def _process_paths(self):
        # Processing of output path.
        # If direction is both and both directions traversed
        if (self.direc_in == "both" and len(self.best_labels["forward"]) > 1 and
                len(self.best_labels["backward"]) > 1):
            # Run path joining procedure.
            self._clean_up_best_labels()
            self._join_paths()
        # If one direction of not both directions traversed,
        else:
            # If forward direction specified or backward direction not traversed
            if (self.direc_in == "forward" or
                (self.direc_in == "both" and
                 len(self.best_labels["backward"]) == 1)):
                # Forward
                self.best_label = self.final_label
            # If backward direction specified or forward direction not traversed
            else:
                # Backward
                self.best_label = self._process_bwd_label(
                    self.final_label, self.min_res_in)

    def _process_bwd_label(self, label, cumulative_res, edge=None):
        # Reverse backward path and inverts resource consumption
        label.path.reverse()
        label.res[0] = self.max_res_in[0] - label.res[0]
        label.res = label.res + cumulative_res
        return label

    def _clean_up_best_labels(self):
        # Removed all dominated labels in best_labels
        for direc in ["forward", "backward"]:
            labels_to_pop = deque()
            for l in self.best_labels[direc]:
                labels_to_pop.extend(
                    self._check_dominance(l, direc, unproc=False, best=True))
            self._remove_labels(labels_to_pop, direc, unproc=False, best=True)

    def _join_paths(self):
        """
        The procedure "Join" or Algorithm 3 from `Righini and Salani (2006)`_.

        Modified to get rid of nested for loops and reduced search.

        :return: list with the final path.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
        """
        log.debug("joining")
        for fwd_label in self.best_labels["forward"]:
            # Create generator for backward labels for current forward label.
            # Includes only those that:
            # 1. Paths can be joined (exists a connecting edge)
            # 2. Introduces no cycles
            # 3. When combined with the forward label, they satisfy the halfway check
            bwd_labels = (l for l in self.best_labels["backward"] if (
                (fwd_label.node, l.node) in self.G.edges() and \
                not any(n in fwd_label.path for n in l.path) and
                self._half_way(fwd_label, l)))
            for bwd_label in bwd_labels:
                # Merge two labels
                merged_label = self._merge_labels(fwd_label, bwd_label)
                # Check resource feasibility
                if (merged_label and merged_label.feasibility_check(
                        self.max_res_in, self.min_res_in)):
                    # Save label
                    self._save(merged_label)

    def _half_way(self, fwd_label, bwd_label):
        """
        Half-way check from `Righini and Salani (2006)`_.
        Checks if a pair of labels is closes to the half-way point.

        :return: bool. True if the half-way check passes, false otherwise.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
        """
        phi = abs(fwd_label.res[0] - (self.max_res_in[0] - bwd_label.res[0]))
        if 0 <= phi <= 2:
            return True
        else:
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
        # Reconstruct edge with edge data
        edge = (fwd_label.node, _bwd_label.node,
                self.G[fwd_label.node][_bwd_label.node])
        # Custom resource merging function
        if self.REF_join:
            final_res = self.REF_join(fwd_label.res, _bwd_label.res, edge)
            self._process_bwd_label(_bwd_label, self.min_res_in)
        # Default resource merging
        else:
            # Extend forward label along joining edge
            label = fwd_label.get_new_label(edge, "forward")
            if not label:
                return
            # Process backward label
            self._process_bwd_label(_bwd_label, label.res)
            final_res = _bwd_label.res
        # Record total weight, total_res and final path
        weight = fwd_label.weight + edge[2]['weight'] + _bwd_label.weight
        final_path = fwd_label.path + _bwd_label.path
        merged_label = Label(weight, "Sink", final_res, final_path)
        return merged_label

    def _save(self, label):
        # Saves a label for exposure
        if not self.best_label or self._full_dominance_check(
                label, self.best_label, "forward"):
            log.debug("Saving label {} as best".format(label))
            log.debug("With path {}".format(label.path))
            self.best_label = label
