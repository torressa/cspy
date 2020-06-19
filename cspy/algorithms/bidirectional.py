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

from cspy.checking import check, check_seed
from cspy.preprocessing import preprocess_graph
from cspy.algorithms.bidirectional_search import Search
from cspy.algorithms.label import Label

LOG = getLogger(__name__)


class BiDirectional:
    """
    Implementation of the bidirectional labeling algorithm with dynamic
    half-way point (`Tilk 2017`_).
    This requires the joining procedure (Algorithm 3) from
    `Righini and Salani (2006)`_, also implemented.
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
        Either "random", "generated" (direction with least number of generated labels),
        "processed" (direction with least number of processed labels), or,
        "unprocessed" (direction with least number of unprocessed labels).
        Default: "random"

    time_limit : int, optional
        time limit in seconds.
        Default: None

    threshold : float, optional
        specify a threshold for a an acceptable resource feasible path.
        This might cause the search to terminate early.
        Default: None

    elementary : bool, optional
        whether the problem is elementary. i.e. no cycles are allowed in the
        final path. Note this may increase run time.
        Default: False

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
        self.random_state = check_seed(seed)
        Label.REF_forward = REF_forward if REF_forward else add
        Label.REF_backward = REF_backward if REF_backward else sub

        self.REF_join = REF_join

        # Algorithm specific attributes #
        self.start_time = None
        self.fwd_search = None
        self.bwd_search = None
        self.current_label = OrderedDict({"forward": None, "backward": None})
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
        # Start up threads
        fwd_thread.start()
        bwd_thread.start()
        # Run searches
        fwd_thread.join(self.time_limit)
        bwd_thread.join(self.time_limit)
        # Terminate threads
        fwd_thread.terminate()
        bwd_thread.terminate()
        # Check if time limit exceeded without finding a path
        _ = self._terminate_serial()

        self._process_paths()
        if self.best_labels is None:
            raise Exception("No resource feasible path has been found")

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

    def _init_parallel(self):
        mgr = Manager()
        # Shared data structures
        self.max_res = mgr.list(self.max_res)
        self.min_res = mgr.list(self.min_res)
        self.best_labels = mgr.dict()

    # Serial Search #

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

    def _terminate_serial(self) -> bool:
        """Check whether time limit is violated or final path with weight
        under the input threshold"""
        if self.time_limit is not None and self._check_time_limit_breached():
            if not self._check_st_final_path():
                raise Exception("Time limit reached without finding a path")
            return True
        if self._check_threshold():
            return True
        return False

    def _check_threshold(self) -> bool:
        """Check if the a final s-t path has been found that has a total weight
        is under the threshold."""
        if self.final_label:
            if self._check_st_final_path():
                if self.threshold is not None and self.final_label.weight < self.threshold:
                    return True
        return False

    def _check_st_final_path(self) -> bool:
        # Check if path in the final label is a valid s-t path.
        if self.final_label:
            return all(_ in self.final_label.path for _ in ["Source", "Sink"])
        return False

    def _check_time_limit_breached(self) -> bool:
        # Check if time_limit has been breached.
        if self.time_limit is not None:
            return self.time_limit - (time() - self.start_time) <= 0.0
        return False

    def _update_current_labels(self):
        self.current_label["forward"] = self.fwd_search.current_label
        self.current_label["backward"] = self.bwd_search.current_label

    def _update_res(self):
        self.min_res = self.fwd_search.get_res()
        self.max_res = self.bwd_search.get_res()

    def _update_best_labels(self):
        self.best_labels["forward"] = self.fwd_search.best_labels
        self.best_labels["backward"] = self.bwd_search.best_labels

    def _update_final_label(self):
        if self.direction == "forward":
            self.final_label = self.fwd_search.final_label
        elif self.direction == "backward":
            self.final_label = self.bwd_search.final_label
        else:
            fwd_final = self.fwd_search.final_label
            bwd_final = self.bwd_search.final_label
            if fwd_final:
                self.final_label = fwd_final
            elif bwd_final:
                self.final_label = bwd_final

    def _get_direction(self):
        """Determine the next search direction (for series search)
        dending on the input method or direction
        """
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
                    return ("forward" if self.fwd_search.generated_count <
                            self.bwd_search.generated_count else "backward")
                elif self.method == "processed":
                    # return direction with least number of processed labels
                    return ("forward" if self.fwd_search.processed_count <
                            self.bwd_search.processed_count else "backward")
                elif self.method == "unprocessed":
                    # return direction with least number of unprocessed labels
                    return ("forward" if self.fwd_search.unprocessed_count <
                            self.bwd_search.unprocessed_count else "backward")
            return
        else:
            if not self.current_label[self.direction]:
                return
            return self.direction

    # Path post-processing #

    def _process_paths(self):
        # Processing of output path.
        if len(self.best_labels["forward"]) > 1 and len(
                self.best_labels["backward"]) > 1:
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
            for label in self.best_labels[direc]:
                labels_to_pop.extend(
                    self._check_dominance(label, direc, unproc=False,
                                          best=True))
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
