from time import time
from copy import deepcopy
from operator import add, sub
from logging import getLogger
from collections import OrderedDict, deque
from typing import List, Dict, Optional, Callable, Union, Tuple

from networkx import DiGraph
from numpy import array, zeros
from numpy.random import RandomState

from cspy.algorithms.label import Label
from cspy.preprocessing import preprocess_graph
from cspy.checking import check, check_seed, check_time_limit_breached

LOG = getLogger(__name__)


class BiDirectional:
    """Implementation of the bidirectional labeling algorithm with dynamic
    half-way point (`Tilk 2017`_).

    Depending on the range of values for bounds for the first resource, we get
    four different algorithms. See ``self.name_algorithm`` and Notes.

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
        Either "random", "generated" (direction with least number of generated
        labels), "processed" (direction with least number of processed labels),
        or, "unprocessed" (direction with least number of unprocessed labels).
        Default: "random"
    time_limit : int, optional
        time limit in seconds.
        Default: None
    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path with
        total cost <= threshold.
        Note this typically causes the search to terminate early.
        Default: None
    elementary : bool, optional
        whether the problem is elementary. i.e. no cycles are allowed in the
        final path. Note this may increase run time.
        Default: False
    dominance_checks : int, optional
        multiple of iterations to run the dominance checks.
        Default : 2 (every second iteration)
    seed : None or int or numpy.random.RandomState instance, optional
        seed for PSOLGENT class. Default : None (which gives a single value
        numpy.random.RandomState).
    REF_forward, REF_backward, REF_join : functions, optional
        Custom resource extension functions. See `REFs`_ for more details.
        Default : additive
    .. _REFs : https://cspy.readthedocs.io/en/latest/how_to.html#refs
    .. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
    .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
    """

    def __init__(self,
                 G: DiGraph,
                 max_res: List[float],
                 min_res: List[float],
                 preprocess: Optional[bool] = False,
                 direction: Optional[str] = "both",
                 method: Optional[str] = "random",
                 time_limit: Optional[float] = None,
                 threshold: Optional[float] = None,
                 elementary: Optional[bool] = False,
                 dominance_frequency: Optional[int] = 1,
                 seed: Union[int, RandomState, None] = None,
                 REF_forward: Optional[Callable] = None,
                 REF_backward: Optional[Callable] = None,
                 REF_join: Optional[Callable] = None):
        # Check inputs
        check(G,
              max_res,
              min_res,
              direction,
              REF_forward=REF_forward,
              REF_backward=REF_backward,
              REF_join=REF_join,
              algorithm=__name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF_forward)

        self.max_res = max_res.copy()
        self.min_res = min_res.copy()
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        self.direction = direction
        self.method = method
        self.time_limit = time_limit
        self.elementary = elementary
        self.threshold = threshold
        self.dominance_frequency = dominance_frequency
        self.random_state = check_seed(seed)
        # Set label class attributes
        Label.REF_forward = REF_forward if REF_forward else add
        Label.REF_backward = REF_backward if REF_backward else sub

        self.REF_join = REF_join

        # Algorithm specific attributes
        self.iteration = 0
        # Containers for labels
        self.current_label: Dict[str, Label] = None
        self.unprocessed_labels: Dict[str, List[Label]] = None
        self.best_labels: Dict[str, List[Label]] = None
        # Containers for counters
        self.unprocessed_counts: Dict[str, int] = 0
        self.processed_counts: Dict[str, int] = 0
        self.generated_counts: Dict[str, int] = 0
        # For exposure
        self.final_label: Label = None
        self.best_label: Label = None
        # Populate containers
        self._init_containers()

    def run(self):
        'Run the algorithm'
        self.start_time = time()
        while self.current_label["forward"] or self.current_label["backward"]:
            if self._terminate():
                break
            direc = self._get_direction()
            if direc:
                self._algorithm(direc)
            else:
                break

        return self._process_paths()

    @property
    def path(self):
        """Get list with nodes in calculated path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.path

    @property
    def total_cost(self):
        """Get accumulated cost along the path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.weight

    @property
    def consumed_resources(self):
        """Get accumulated resources consumed along the path.
        """
        if not self.best_label:
            raise Exception("Please call the .run() method first")
        return self.best_label.res

    def name_algorithm(self):
        """Given the resource bounds, prints which algorithm will run.
        """
        HF, HB = self.max_res[0], self.min_res[0]
        if self.direction == "forward":
            print("Monodirectional forward labeling algorithm")
        elif self.direction == "backward":
            LOG.info("Monodirectional backward labeling algorithm")
        elif HF > HB:
            print("Bidirectional labeling algorithm with" +
                  " dynamic halfway point")
        else:
            print("The algorithm can't move in either direction!")

    # Private methods #

    # Initialisations #

    def _init_containers(self):
        'Initialise containers (labels and counters)'
        # set minimum bounds if not all 0
        if not all(m == 0 for m in self.min_res):
            self.min_res = zeros(len(self.min_res))
        bwd_start = self.min_res.copy()
        bwd_start[0] = self.max_res[0]

        self.current_label = OrderedDict({
            "forward": Label(0, "Source", self.min_res, ["Source"]),
            "backward": Label(0, "Sink", bwd_start, ["Sink"])
        })
        self.unprocessed_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # Best labels
        self.best_labels = OrderedDict({
            "forward": deque([self.current_label["forward"]]),
            "backward": deque([self.current_label["backward"]])
        })
        # Counters
        self.unprocessed_counts = OrderedDict({"forward": 0, "backward": 0})
        self.processed_counts = OrderedDict({"forward": 0, "backward": 0})
        self.generated_counts = OrderedDict({"forward": 0, "backward": 0})

    # Algorithm #

    def _terminate(self) -> bool:
        """Check whether time limit is violated or final path with weight
        under the input threshold"""
        if self.time_limit is not None and check_time_limit_breached(
                self.start_time, self.time_limit):
            return True
        if self._check_final_label():
            return True
        return False

    def _check_final_label(self) -> bool:
        """Check if the final label contains an s-t path with total weight that
        is under the threshold."""
        if self.final_label:
            if (self.threshold is not None and
                    self.final_label.check_threshold(self.threshold) and
                    self.final_label.check_st_path()):
                return True
        return False

    def _get_direction(self) -> Union[str, None]:
        """Returns which direction should be searched next
        None at termination.
        """
        if self.direction == "both":
            if (self.current_label["forward"] and
                    not self.current_label["backward"]):
                return "forward"
            elif (not self.current_label["forward"] and
                  self.current_label["backward"]):
                return "backward"
            elif self.current_label["forward"]:
                if self.method == "random":
                    # return a random direction
                    return self.random_state.choice(["forward", "backward"])
                elif self.method == "unprocessed":
                    # return direction with least number of unprocessed_labels labels
                    return ("forward" if self.unprocessed_counts["forward"] <
                            self.unprocessed_counts["backward"] else "backward")
                elif self.method == "processed":
                    # return direction with least number of processed labels
                    return ("forward" if self.processed_counts["forward"] <
                            self.processed_counts["backward"] else "backward")
                elif self.method == "generated":
                    # return direction with least number of generated labels
                    return ("forward" if self.generated_counts["forward"] <
                            self.generated_counts["backward"] else "backward")
            else:  # if both are empty
                return None
        else:
            if not (self.current_label["forward"] or
                    self.current_label["backward"]):
                return None
            elif not self.current_label[self.direction]:
                return None
            return self.direction

    def _algorithm(self, direc):
        'Algorithm step wrapper'
        if direc == "forward":  # forward
            # Update backwards half-way point
            self.min_res[0] = max(
                self.min_res[0],
                min(self.current_label[direc].res[0], self.max_res[0]))
        else:  # backward
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0],
                max(self.current_label[direc].res[0], self.min_res[0]))
        self._propagate_label(direc)
        # Extend label
        next_label = self._get_next_label(direc)
        self.current_label[direc] = next_label
        if self.iteration % self.dominance_frequency == 0:
            self._check_dominance(next_label, direc)
        self.processed_counts[direc] += 1
        self.iteration += 1

    def _propagate_label(self, direc):
        'Propagate current label along all suitable edges in current direction'
        idx = 0 if direc == "forward" else 1
        for edge in (e for e in self.G.edges(data=True)
                     if e[idx] == self.current_label[direc].node):
            new_label = self.current_label[direc].get_new_label(edge, direc)
            # If the new label is resource feasible
            if new_label and new_label.feasibility_check(
                    self.max_res, self.min_res):
                # And is not already in the unprocessed labels list
                if new_label not in self.unprocessed_labels[direc]:
                    self.unprocessed_labels[direc].append(new_label)
                    self.unprocessed_counts[direc] += 1

    def _get_next_label(self, direc):
        current_label = self.current_label[direc]
        unproc_labels = self.unprocessed_labels[direc]

        self.generated_counts[direc] += 1
        self._remove_labels([current_label], direc)
        # Return label with minimum monotone resource for the forward search
        # and the maximum monotone resource for the backward search
        if unproc_labels:
            if direc == "forward":
                return min(unproc_labels, key=lambda x: x.res[0])
            return max(unproc_labels, key=lambda x: x.res[0])
        return None

    def _check_dominance(self, label_to_check, direc, best=False):
        """For all labels, checks if ``label_to_check`` is dominated,
        or itself dominates any other label in either the unprocessed_labels
        list or the non-dominated labels list.
        If this is found to be the case, the dominated label(s) is(are)
        removed from the appropriate list.
        """
        # Select appropriate list to check
        if not best:
            labels_to_check = self.unprocessed_labels[direc]
        else:
            labels_to_check = self.best_labels[direc]
        # If label is not None (at termination)
        if label_to_check:
            # Gather all comparable labels (same node)
            all_labels = deque(
                l for l in labels_to_check
                if l.node == label_to_check.node and l != label_to_check)
            # Add to list for removal if they are dominated
            labels_to_pop = deque(
                l for l in all_labels
                if label_to_check.dominates(l, direc) and label_to_check.
                feasibility_check(self.max_res_in, self.min_res_in))
            # Add input label for removal if itself is dominated
            if any((l.dominates(label_to_check, direc) and
                    l.feasibility_check(self.max_res_in, self.min_res_in))
                   for l in all_labels):
                labels_to_pop.append(label_to_check)
            elif not best:
                # check and save current label
                self._save_current_best_label(direc)
            # if unprocessed labels checked then remove labels_to_pop
            if not best:
                self._remove_labels(labels_to_pop, direc, best)
            # Otherwise, return labels_to_pop for later removal
            else:
                return labels_to_pop

    def _remove_labels(self,
                       labels_to_pop: List[Tuple[Label, bool]],
                       direc: str,
                       best: bool = False):
        """Remove all labels in ``labels_to_pop`` from either the array of
        unprocessed labels or the array of non-dominated labels
        """
        # Remove all processed labels from unprocessed dict
        for label_to_pop in deque(set(labels_to_pop)):
            if not best and label_to_pop in self.unprocessed_labels[direc]:
                idx = self.unprocessed_labels[direc].index(label_to_pop)
                del self.unprocessed_labels[direc][idx]
            if best and label_to_pop in self.best_labels[direc]:
                idx = self.best_labels[direc].index(label_to_pop)
                del self.best_labels[direc][idx]

    def _save_current_best_label(self, direc):
        current_label = self.current_label[direc]
        final_label = self.final_label

        self.best_labels[direc].append(current_label)

        if not final_label:
            self.final_label = current_label
            return

        # If not resource feasible wrt input resource bounds
        if not current_label or not current_label.feasibility_check(
                self.max_res_in, self.min_res_in):
            return

        try:
            if current_label.full_dominance(final_label, direc):
                self.final_label = current_label
        except TypeError:
            # Labels are not comparable i.e. Belong to different nodes
            if (direc == "forward" and (current_label.path[-1] == "Sink" or
                                        final_label.node == "Source")):
                self.final_label = current_label
            elif (direc == "backward" and (current_label.path[-1] == "Source" or
                                           final_label.node == "Sink")):
                self.final_label = current_label

    # Post processing #

    def _process_paths(self):
        'Processing of output path.'
        # If direction is both and both directions traversed
        if (self.direction == "both" and
                len(self.best_labels["forward"]) > 1 and
                len(self.best_labels["backward"]) > 1):
            # Run path joining procedure.
            self._clean_up_best_labels()
            self._join_paths()
        # If one direction of not both directions traversed,
        else:
            # If forward direction specified or backward direction not traversed
            if (self.direction == "forward" or
                (self.direction == "both" and
                 len(self.best_labels["backward"]) == 1)):
                # Forward
                self.best_label = self.final_label
            # If backward direction specified or forward direction not traversed
            else:
                # Backward
                self.best_label = self._process_bwd_label(self.final_label,
                                                          self.min_res_in,
                                                          invert_min_res=True)

    def _process_bwd_label(self,
                           label,
                           cumulative_res=None,
                           invert_min_res=False):
        'Reverse backward path and inverts resource consumption'
        label.path.reverse()
        label.res[0] = self.max_res_in[0] - label.res[0]
        if cumulative_res is not None:
            label.res = label.res + cumulative_res
        if invert_min_res:
            label.res[1:] = label.res[1:] - self.min_res_in[1:]
        return label

    def _clean_up_best_labels(self):
        'Remove all dominated labels in best_labels'
        for direc in ["forward", "backward"]:
            labels_to_pop = deque()
            for label in self.best_labels[direc]:
                labels_to_pop.extend(
                    self._check_dominance(label, direc, best=True))
            self._remove_labels(labels_to_pop, direc, best=True)

    def _join_paths(self):
        """The procedure "Join" or Algorithm 3 from
        `Righini and Salani (2006)`_.
        Modified to get rid of nested for loops and reduced search.

        :return: list with the final path.
        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
        """
        LOG.debug("joining")
        for fwd_label in self.best_labels["forward"]:
            # Create generator for backward labels for current forward label.
            # Includes only those that:
            # 1. Paths can be joined (exists a connecting edge)
            # 2. Introduces no cycles
            # 3. When combined with the forward label, they satisfy the halfway check
            bwd_labels = (l for l in self.best_labels["backward"]
                          if (fwd_label.node, l.node) in self.G.edges() and all(
                              n not in fwd_label.path
                              for n in l.path) and self._half_way(fwd_label, l))
            for bwd_label in bwd_labels:
                # Merge two labels
                merged_label = self._merge_labels(fwd_label, bwd_label)
                # Check resource feasibility
                if (merged_label and merged_label.feasibility_check(
                        self.max_res_in, self.min_res_in)):
                    # Save label
                    self._join_save(merged_label)

    def _half_way(self, fwd_label, bwd_label):
        """Checks if a pair of labels is closes to the half-way point.
        """
        phi = abs(fwd_label.res[0] - (self.max_res_in[0] - bwd_label.res[0]))
        return 0 <= phi <= 2

    def _merge_labels(self, fwd_label, bwd_label):
        """Merge labels produced by a backward and forward label.

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
        return Label(weight, "Sink", final_res, final_path)

    def _join_save(self, label):
        'Saves a label for exposure'
        if not self.best_label or label.full_dominance(self.best_label,
                                                       "forward"):
            LOG.debug("Saving path %s as best, with weight %s", label.path,
                      label.weight)
            self.best_label = label
