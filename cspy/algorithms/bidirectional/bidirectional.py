import sys
from time import time
from copy import deepcopy
from operator import add, sub
from logging import getLogger
from typing import List, Union, Optional, Callable
from collections import OrderedDict, deque
from multiprocessing import Process, Manager

from numpy import array
from numpy.random import RandomState
from networkx import DiGraph

# Module level imports
from cspy.checking import check
from cspy.preprocessing import preprocess_graph

# Local imports
from .search import Search
from .label import Label

LOG = getLogger(__name__)


class BiDirectional:

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
        # Init with seed if given
        if seed is None:
            self.random_state = RandomState()
        elif isinstance(seed, int):
            self.random_state = RandomState(seed)
        elif isinstance(seed, RandomState):
            self.random_state = seed
        else:
            raise Exception("{} cannot be used to seed".format(seed))
        # If given, set REFs for dominance relations and feasibility checks
        Label._REF_forward = REF_forward if REF_forward else add
        Label._REF_backward = REF_backward if REF_backward else sub
        self.REF_join = REF_join

        # Algorithm specific attributes #
        self.start_time = None
        self.fwd_search = None
        self.bwd_search = None
        self.current_label = OrderedDict()
        # Unprocessed label counts
        self.unprocessed_labels = OrderedDict({"forward": 0, "backward": 0})
        # Generated label counts
        self.generated_labels = OrderedDict({"forward": 0, "backward": 0})
        # To save all best labels
        self.final_label = None
        self.best_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        self.best_label = None

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

    def run(self):
        """Find shortest path with resource constraints in series.
        """
        self._init_searches()
        self._update_current_labels()
        while self.current_label["forward"] or self.current_label["backward"]:
            direc = self._get_direction()
            if direc:
                self._move(direc)
            else:
                break
            if self._terminate_serial():
                break
        self._process_paths()
        if self.best_label is None:
            raise Exception("No resource feasible path has been found")

    def run_parallel(self):
        """Find shortest path with resource constraints in parallel.
        """
        self._init_searches()
        self._init_parallel()
        fwd_thread = Process(target=self.fwd_search.run_parallel,
                             args=(self.max_res, self.best_labels))
        bwd_thread = Process(target=self.bwd_search.run_parallel,
                             args=(self.min_res, self.best_labels))
        fwd_thread.start()
        bwd_thread.start()
        fwd_thread.join(self.time_limit)
        bwd_thread.join(self.time_limit)

        self._process_paths()

    def name_algorithm(self):
        """Determine which algorithm is running.
        Logs algorithm classification at INFO level.
        """
        HF, HB = self.max_res[0], self.min_res[0]
        if self.direction == "forward":
            LOG.info("Monodirectional forward labeling algorithm")
        elif self.direction == "backward":
            LOG.info("Monodirectional backward labeling algorithm")
        elif HF > HB:
            LOG.info(
                "Bidirectional labeling algorithm with dynamic halfway point")
        else:
            LOG.info("The algorithm can't move in either direction!")

    # Private methods #

    def _init_searches(self):
        self.start_time = time()
        # Initialise forward search
        self.fwd_search = Search(self.G, self.max_res, self.min_res, "forward",
                                 self.elementary)
        # initialise backward search
        self.bwd_search = Search(self.G, self.max_res, self.min_res, "backward",
                                 self.elementary)

    # Parallel private methods #

    def _init_parallel(self):
        mgr = Manager()
        self.max_res = mgr.list(self.max_res)
        self.min_res = mgr.list(self.min_res)
        self.best_labels = mgr.dict()

    # Standard Search private methods #

    def _move(self, direc):
        self._update_current_labels()
        self._update_res()
        if self.direction == "both":
            self._update_best_labels()
        self._update_final_label()
        if self.current_label["forward"] and direc == "forward":
            self.fwd_search.move(self.max_res)
        elif self.current_label["backward"] and direc == "backward":
            self.bwd_search.move(self.min_res)

    def _terminate_serial(self):
        if self.time_limit is not None and self._get_time_remaining() <= 0:
            return True
        if self.final_label and self.threshold is not None and (
                self.final_label.weight < self.threshold and
                all(_ in self.final_label.path for _ in ["Source", "Sink"])):
            return True
        return False

    def _get_time_remaining(self):
        # Returns time remaining in seconds or None if no time limit set.
        if self.time_limit is not None:
            return self.time_limit - (time() - self.start_time)
        return None

    def _update_current_labels(self):
        self.current_label["forward"] = self.fwd_search.get_current_label()
        self.current_label["backward"] = self.bwd_search.get_current_label()

    def _update_res(self):
        self.min_res = self.fwd_search.get_res()
        self.max_res = self.bwd_search.get_res()

    def _update_best_labels(self):
        self.best_labels["forward"] = self.fwd_search.get_best_labels()
        self.best_labels["backward"] = self.bwd_search.get_best_labels()

    def _update_unprocessed_count(self):
        self.unprocessed_labels[
            "forward"] = self.fwd_search.get_unprocessed_count()
        self.unprocessed_labels[
            "backward"] = self.bwd_search.get_unprocessed_count()

    def _update_generated_count(self):
        self.generated_labels["forward"] = self.fwd_search.get_generated_count()
        self.generated_labels["backward"] = self.bwd_search.get_generated_count(
        )

    def _update_final_label(self):
        if self.direction == "forward":
            self.final_label = self.fwd_search.get_final_label()
        elif self.direction == "backward":
            self.final_label = self.bwd_search.get_final_label()
        else:
            fwd_final = self.fwd_search.get_final_label()
            bwd_final = self.bwd_search.get_final_label()
            if fwd_final:
                self.final_label = fwd_final
            elif bwd_final:
                self.final_label = self._process_bwd_label(bwd_final)

    def _get_direction(self):
        if self.direction == "both":
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
                    return ("forward" if self.unprocessed_labels["forward"] <
                            self.unprocessed_labels["backward"] else "backward")
            return
        else:
            if (not self.current_label["forward"] and
                    not self.current_label["backward"]):
                return
            elif not self.current_label[self.direction]:
                return
            return self.direction

    # Path post-processing #

    def _process_paths(self):
        # Processing of output path.
        if (self.best_labels["forward"] and self.best_labels["backward"]):
            # If bi-directional algorithm used, run path joining procedure.
            # self._clean_up_best_labels()
            self._join_paths()
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
        # Reverse backward path and inverts resource consumption
        label.path.reverse()
        label.res[0] = self.max_res_in[0] - label.res[0]
        if cumulative_res is not None:
            label.res = label.res + cumulative_res
        if invert_min_res:
            label.res[1:] = label.res[1:] - self.min_res_in[1:]
        return label

    def _clean_up_best_labels(self):
        # Remove all dominated labels in best_labels
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
                    self._save(merged_label)
                    # Stop if threshold specified and label is under
                    if self.threshold is not None and merged_label.weight <= self.threshold:
                        return

    def _half_way(self, fwd_label, bwd_label):
        """
        Half-way check from `Righini and Salani (2006)`_.
        Checks if a pair of labels is closes to the half-way point.

        :return: bool. True if the half-way check passes, false otherwise.

        .. _Righini and Salani (2006): https://www.sciencedirect.com/science/article/pii/S1572528606000417
        """
        phi = abs(fwd_label.res[0] - (self.max_res_in[0] - bwd_label.res[0]))
        return 0 <= phi <= 2

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
                return None
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
        if not self.best_label or label.full_dominance(self.best_label,
                                                       "forward"):
            LOG.debug("Saving label %s as best", label)
            LOG.debug("With path %s", label.path)
            self.best_label = label
