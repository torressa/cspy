from logging import getLogger
from collections import OrderedDict, deque

from numpy import array, zeros

# Local module imports
from .label import Label

LOG = getLogger(__name__)


class Search:
    """
    Helper class to advance the search in either direction.
    """

    def __init__(self, G, max_res, min_res, direction, elementary):
        self.G = G
        self.max_res, self.min_res = max_res.copy(), min_res.copy()
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        self.direction = direction
        self.elementary = elementary
        # Algorithm specific attributes #
        self.current_label = None
        self.unprocessed_labels = OrderedDict()
        self.best_labels = deque()
        self.generated_labels_count = 0
        self.final_label = None

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

    def get_current_label(self):
        """Return current position (label) of search.
        """
        return self.current_label

    def get_res(self):
        """Return current resource bounds.
        """
        if self.direction == "forward":
            return self.min_res
        return self.max_res

    def get_unprocessed_count(self):
        """Get current number of labels to be processed
        """
        return len(self.unprocessed_labels)

    def get_generated_count(self):
        """Get number of labels that have been generated
        """
        return self.generated_labels_count

    def get_best_labels(self):
        """Get list of "best" non-dominanted labels.
        """
        return self.best_labels

    def get_final_label(self):
        """Get current number of labels to be processed
        """
        return self.final_label

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
        if self.direction == "forward":  # forward
            idx = 0  # index for head node
            # Update backwards half-way point
            self.min_res[0] = max(
                self.min_res[0], min(self.current_label.res[0],
                                     self.max_res[0]))
            LOG.debug("HB = %s", self.min_res[0])
        else:  # backward
            idx = 1  # index for tail node
            # Update forwards half-way point
            self.max_res[0] = min(
                self.max_res[0], max(self.current_label.res[0],
                                     self.min_res[0]))
            LOG.debug("HF = %s", self.max_res[0])
        # Initialise label deque
        if self.current_label not in self.unprocessed_labels:
            self.unprocessed_labels[self.current_label] = deque()
        # Select edges with the same head/tail node as the current label node.
        edges = deque(e for e in self.G.edges(data=True)
                      if e[idx] == self.current_label.node)
        # If Label not been seen before, initialise a list
        # Propagate current label along all suitable edges in current direction
        for edge in edges:
            self._propagate_label(edge)
        LOG.debug("Unprocessed labels = %s", self.unprocessed_labels)
        self._clean_up_unprocessed_labels()
        # Extend label
        next_label = self._get_next_label()
        # Update current label
        self.current_label = next_label
        # Dominance checks
        self._check_dominance(next_label)

    def _propagate_label(self, edge):
        # Label propagation #
        new_label = self.current_label.get_new_label(edge, self.direction)
        # If the new label is resource feasible
        if new_label and new_label.feasibility_check(self.max_res, self.min_res,
                                                     self.direction):
            # And is not already in the unprocessed labels list
            if not any(new_label == l
                       for l in self.unprocessed_labels[self.current_label]):
                self.unprocessed_labels[self.current_label].append(new_label)

    def _clean_up_unprocessed_labels(self):
        self._remove_labels([(self.current_label, False)])
        self._remove_labels((k, True)
                            for k, v in self.unprocessed_labels.items()
                            if len(v) == 0)

    def _get_next_label(self, exclude_label=None):
        if self.current_label in self.unprocessed_labels:
            unproc_sub_labels = deque(
                l for l in self.unprocessed_labels[self.current_label]
                if l != exclude_label)
        else:
            unproc_sub_labels = None

        if self.current_label and unproc_sub_labels:
            LOG.debug("processing sub labels from %s", self.current_label)
            unproc_labels = unproc_sub_labels
        else:
            LOG.debug("processing labels from unprocessed")
            unproc_labels = deque(k for k, v in self.unprocessed_labels.items()
                                  if k != exclude_label)

        self.generated_labels_count += 1
        # Return label with minimum monotone resource for the forward search
        # and the maximum monotone resource for the backward search
        if unproc_labels:
            if self.direction == "forward":
                return min(unproc_labels, key=lambda x: x.weight)
            return min(unproc_labels, key=lambda x: x.weight)
        return None

    # Dominance #

    def _check_dominance(self, label_to_check):
        """
        For all labels, checks if ``label_to_check`` is dominated,
        or itself dominates any other label in either the unprocessed_labels
        list or the non-dominated labels list.
        If this is found to be the case, the dominated label(s) is(are)
        removed from the appropriate list.
        """
        # Select appropriate list to check
        LOG.debug("Dominance")
        labels_to_check = deque(
            l for l in self.unprocessed_labels
            if l != label_to_check and l.node == label_to_check.node)
        labels_to_check.extend(
            l for k, v in self.unprocessed_labels.items() for l in v
            if l != label_to_check and l.node == label_to_check.node)
        # If label is not None (at termination)
        if label_to_check and label_to_check.feasibility_check(
                self.max_res_in, self.min_res_in, self.direction):
            # Add to list for removal if they are dominated
            if not self.elementary:
                # Completely remove label if non-elementary
                labels_to_pop = deque(
                    (l, True)
                    for l in labels_to_check
                    if label_to_check.dominates(l, self.direction))
            else:
                # Completely remove label if elementary and subset condition
                labels_to_pop = deque(
                    (l, label_to_check.subset(l))
                    for l in labels_to_check
                    if label_to_check.dominates(l, self.direction))

            # Add input label for removal if itself is dominated
            if any(
                    l.dominates(label_to_check, self.direction)
                    for l in labels_to_check):

                if not self.elementary:
                    destroy = True
                destroy = any(
                    l.subset(label_to_check)
                    for l in labels_to_check
                    if l.dominates(label_to_check, self.direction))
                labels_to_pop.append((label_to_check, destroy))
            else:
                # check and save current label
                self._save_current_best_label()
            self._remove_labels(labels_to_pop, dominance=True)

    def _remove_labels(self, labels_to_pop, dominance=False):
        """
        Remove all labels in ``labels_to_pop`` from either the array of
        unprocessed labels or the array of non-dominated labels

        ``labels_to_pop`` is a list of tuples with (label: Label, destroy: bool).
        The destroy bool, determines if the label and all of its existing extensions
        can be removed.
        """
        # Remove all processed labels from unprocessed dict
        LOG.debug("Removing labels : %s", labels_to_pop)
        for label_to_pop, destroy in deque(set(labels_to_pop)):
            if destroy and label_to_pop in self.unprocessed_labels:
                del self.unprocessed_labels[label_to_pop]
                LOG.debug("Deleted %s", label_to_pop)
            for k, sub_deque in self.unprocessed_labels.items():
                if label_to_pop in sub_deque:
                    _idx = sub_deque.index(label_to_pop)
                    del self.unprocessed_labels[k][_idx]
                    LOG.debug("Key %s removed from sub deque", label_to_pop)
            if dominance and label_to_pop in self.best_labels:
                idx = self.best_labels.index(label_to_pop)
                del self.best_labels[idx]
                LOG.debug("Deleted from best_labels %s", label_to_pop)

    def _save_current_best_label(self):
        """Save labels depending on the current state of the search.
        """
        self.best_labels.append(self.current_label)
        # If first label
        if not self.final_label:
            self.final_label = self.current_label
            LOG.debug("Saved %s as initial best label.", self.current_label)
            return
        # Otherwise, check dominance and replace
        try:
            if self.current_label.full_dominance(self.final_label,
                                                 self.direction):
                LOG.debug("Saving %s as best, with path %s", self.current_label,
                          self.current_label.path)
                self.final_label = self.current_label
        except TypeError:
            # Labels are not comparable i.e. Belong to different nodes
            if (self.direction == "forward" and
                (self.current_label.path[-1] == "Sink" or
                 self.final_label.node == "Source")):
                LOG.debug("Saving %s as best, with path %s", self.current_label,
                          self.current_label.path)
                self.final_label = self.current_label
            elif (self.direction == "backward" and
                  (self.current_label.path[-1] == "Source" or
                   self.final_label.node == "Sink")):
                LOG.debug("Saving %s as best, with path %s", self.current_label,
                          self.current_label.path)
                self.final_label = self.current_label
