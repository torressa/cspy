from logging import getLogger
from collections import OrderedDict, deque
from typing import List, Tuple, Dict

from networkx import DiGraph
from numpy import array, zeros

from cspy.algorithms.label import Label

LOG = getLogger(__name__)


class Search:
    """
    Helper class to advance the search in either direction.
    """

    def __init__(self, G: DiGraph, max_res: List[float], min_res: List[float],
                 direction: str, elementary: bool):
        self.G = G
        self.max_res, self.min_res = max_res.copy(), min_res.copy()
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        self.direction = direction
        self.elementary = elementary
        # Algorithm specific attributes #
        self.current_label: Label = None
        self.unprocessed_labels: Dict[Label, Dict[List[Label]]] = OrderedDict()
        self.best_labels: List = deque()
        self.unprocessed_count: int = 0
        self.processed_count: int = 0
        self.generated_count: int = 0
        self.final_label: Label = None

        self._init_labels()

    def run_parallel(self, res_bound, results):
        """Method for internal use for parallel search.
        ``res_bound`` is a shared array.
        ``results`` is a shared dict.
        """
        while self.current_label:
            self.move(res_bound)
        results[self.direction] = self.best_labels

    def move(self, res_bound):
        """Single step for a search in either direction.
        """
        if self.direction == "forward":
            self.max_res = res_bound
        else:
            self.min_res = res_bound
        self._algorithm()

    # getter methods #

    def get_res(self):
        """Return current resource bounds.
        """
        if self.direction == "forward":
            return self.min_res
        return self.max_res

    def clean_up_best_labels(self):
        # Remove all dominated labels in best_labels
        labels_to_pop = deque()
        for label in self.best_labels:
            labels_to_pop.extend(self._check_dominance(label, best=True))
        self._remove_labels(labels_to_pop, dominance=True)

    # Private methods #

    def _init_labels(self):
        # set minimum bounds if not all 0
        if not all(m == 0 for m in self.min_res):
            self.min_res = zeros(len(self.min_res))
        # current forward and backward labels
        if self.direction == "forward":
            self.current_label = Label(0, "Source", self.min_res, ["Source"])
        else:
            bwd_start = self.min_res.copy()
            bwd_start[0] = self.max_res[0]
            self.current_label = Label(0, "Sink", bwd_start, ["Sink"])
        self.best_labels.append(self.current_label)

    def _algorithm(self):
        LOG.debug("Current path = %s, weight = %s", self.current_label.path,
                  self.current_label.weight)
        if self.direction == "forward":  # forward
            idx = 0  # index for tail node
            # Update backwards half-way point
            self.min_res[0] = max(
                self.min_res[0], min(self.current_label.res[0],
                                     self.max_res[0]))
            LOG.debug("HB = %s", self.min_res[0])
        else:  # backward
            idx = 1  # index for head node
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0], max(self.current_label.res[0],
                                     self.min_res[0]))
            LOG.debug("HF = %s", self.max_res[0])
        # Initialise label deque
        if self.current_label not in self.unprocessed_labels:
            self.unprocessed_labels[self.current_label] = deque()
            self.unprocessed_count += 1
        # Select edges with the same head/tail node as the current label node.
        edges = deque(e for e in self.G.edges(data=True)
                      if e[idx] == self.current_label.node)
        # If Label not been seen before, initialise a list
        # Propagate current label along all suitable edges in current direction
        for edge in edges:
            self._propagate_label(edge)
        self._clean_up_unprocessed_labels()
        # Extend label
        next_label = self._get_next_label()
        # If next label already been processed get another one.
        # Repeat until all labels have been checked.
        while True:
            if next_label and next_label.seen:
                next_label = self._get_next_label(next_label)
            elif next_label is None or next_label:
                break
        self.current_label = next_label  # Replace current label
        # Dominance
        self._check_dominance(next_label)

    def _propagate_label(self, edge):
        # Label propagation #
        new_label = self.current_label.get_new_label(edge, self.direction)
        # If the new label is resource feasible
        if new_label and new_label.feasibility_check(self.max_res,
                                                     self.min_res):
            # And is not already in the unprocessed labels list
            if new_label not in self.unprocessed_labels[self.current_label]:
                self.unprocessed_labels[self.current_label].append(new_label)
                self.generated_count += 1

    def _clean_up_unprocessed_labels(self):
        self._remove_labels([(self.current_label, False)])
        self._remove_labels((k, True)
                            for k, v in self.unprocessed_labels.items()
                            if len(v) == 0)

    def _get_next_label(self, exclude_label: Label = None) -> Label:
        try:
            # Get labels from the current one
            _labels = deque(
                l for l in self.unprocessed_labels[self.current_label]
                if l != exclude_label)
        except ValueError:
            # No more labels under current label
            self.current_label.seen = True  # Update current label as seen
            self.processed_count += 1
            _labels = deque(
                l for l in self.unprocessed_labels if l != exclude_label)
        except KeyError:
            # No more label keys, so look at sub lists
            _labels = deque(l for k, v in self.unprocessed_labels.items()
                            for l in v if l != exclude_label)
        if _labels:
            return min(_labels, key=lambda x: x.weight)
        # No more labels to be processed
        return None

    # Dominance #

    def _check_dominance(self, label_to_check: Label, best=False):
        """For all labels, checks if ``label_to_check`` is dominated,
        or itself dominates any other label in either the unprocessed_labels
        dict. If this is found to be the case, the dominated label(s) is(are)
        removed.
        """
        if label_to_check:
            # Select appropriate list to check
            if not best:
                all_labels = self.unprocessed_labels
            else:
                all_labels = self.best_labels
            labels_to_check = deque(
                l for l in all_labels
                if l != label_to_check and l.node == label_to_check.node)
            if not best:
                # Also check sub lists
                labels_to_check.extend(
                    l for k, v in all_labels.items() for l in v
                    if l != label_to_check and l.node == label_to_check.node)
            # Add to list for removal if they are dominated
            labels_to_pop = deque(
                (l, self._check_destroy(label_to_check, l))
                for l in labels_to_check
                if label_to_check.dominates(l, self.direction, self.elementary))
            # Add input label for removal if itself is dominated
            if any(
                    l.dominates(label_to_check, self.direction, self.elementary)
                    for l in labels_to_check):
                destroy = any(
                    self._check_destroy(l, label_to_check)
                    for l in labels_to_check
                    if l.dominates(label_to_check, self.direction,
                                   self.elementary))
                labels_to_pop.append((label_to_check, destroy))
            # Otherwise, save it
            elif not best:
                self._save_current_best_label()
            if not best:
                self._remove_labels(labels_to_pop, dominance=True)
            else:
                return labels_to_pop

    def _check_destroy(self,
                       label1: Label = None,
                       label2: Label = None) -> bool:
        """Determine if label2 and all of its extensions can be removed.
        For the elementary case, label1 dominates label2.
        For the non-elementary case, label1 is not required as the subset
        condition does not have to be met.
        """
        if self.elementary:
            # if the path of label2 is a subset of the path of label1
            # and label2 is resource feasible wrt input bounds
            return (label1.is_path_subset(label2) and
                    label2.feasibility_check(self.max_res_in, self.min_res_in))
        return label2.feasibility_check(self.max_res_in, self.min_res_in)

    def _remove_labels(self, labels_to_pop, dominance=False):
        """
        Remove all labels in ``labels_to_pop`` from either the array of
        unprocessed labels or the array of non-dominated labels

        ``labels_to_pop`` is a list of tuples with (label: Label, destroy: bool).
        The destroy bool, determines if the label and all of its existing extensions
        can be removed.
        """
        # Remove all processed labels from unprocessed dict
        for label_to_pop, destroy in deque(set(labels_to_pop)):
            if destroy and label_to_pop in self.unprocessed_labels:
                del self.unprocessed_labels[label_to_pop]
            if dominance and label_to_pop in self.best_labels:
                idx = self.best_labels.index(label_to_pop)
                del self.best_labels[idx]
                return
            for k, sub_deque in self.unprocessed_labels.items():
                if label_to_pop in sub_deque:
                    _idx = sub_deque.index(label_to_pop)
                    del self.unprocessed_labels[k][_idx]

    def _save_current_best_label(self):
        """Save labels depending on the current state of the search.
        """
        self.best_labels.append(self.current_label)
        if not self.final_label:
            self.final_label = self.current_label
            return
        # If not resource feasible wrt input resource bounds
        if not self.current_label or not self.current_label.feasibility_check(
                self.max_res_in, self.min_res_in):
            return
        # Otherwise, check dominance and replace
        try:
            if self.current_label.full_dominance(self.final_label,
                                                 self.direction):
                self.final_label = self.current_label
        except TypeError:
            # Labels are not comparable i.e. Belong to different nodes
            if (self.direction == "forward" and
                (self.current_label.path[-1] == "Sink" or
                 self.final_label.node == "Source")):
                self.final_label = self.current_label
            elif (self.direction == "backward" and
                  (self.current_label.path[-1] == "Source" or
                   self.final_label.node == "Sink")):
                self.final_label = self.current_label
