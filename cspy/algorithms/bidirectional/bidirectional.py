import sys
from copy import deepcopy
from itertools import repeat
from operator import add, sub
from logging import getLogger
from collections import OrderedDict, deque
from multiprocessing import Process, Manager

from numpy import array, zeros
from numpy.random import RandomState

# Module level imports
from cspy.checking import check
from cspy.preprocessing import preprocess_graph

# Local imports
from .search import Search
from .label import Label

log = getLogger(__name__)


class BiDirectional:

    def __init__(self,
                 G,
                 max_res,
                 min_res,
                 preprocess=False,
                 direction="both",
                 method="random",
                 seed=None,
                 time_limit=None,
                 elementary=False,
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
              algorithm=__name__)
        # Preprocess graph
        self.G = preprocess_graph(G, max_res, min_res, preprocess, REF_forward)
        self.REF_join = REF_join

        self.max_res = max_res.copy()
        self.min_res = min_res.copy()
        self.max_res_in, self.min_res_in = array(max_res.copy()), array(
            min_res.copy())
        self.direction = direction
        self.method = method
        self.time_limit = time_limit

        # Algorithm specific attributes #
        self.current_label = OrderedDict()
        # Initialise forward search
        self.fwd_search = Search(self.G, max_res, min_res, "forward",
                                 elementary, REF_forward, REF_backward)
        # initialise backward search
        self.bwd_search = Search(self.G, max_res, min_res, "backward",
                                 elementary, REF_forward, REF_backward)
        # To save all best labels
        self.best_labels = OrderedDict({
            "forward": deque(),
            "backward": deque()
        })
        # If given, set REFs for dominance relations and feasibility checks
        if REF_forward:
            Label._REF_forward = REF_forward
        else:
            Label._REF_forward = add
        if REF_backward:
            Label._REF_backward = REF_backward
        else:
            Label._REF_backward = sub
        self.best_label = None
        # Init with seed if given
        if seed is None:
            self.random_state = RandomState()
        elif isinstance(seed, int):
            self.random_state = RandomState(seed)
        elif isinstance(seed, RandomState):
            self.random_state = seed
        else:
            raise Exception("{} cannot be used to seed".format(seed))

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

    def run(self):
        # Current forward and backward labels
        self._update_current_labels()
        while self.current_label["forward"] or self.current_label["backward"]:
            direc = self._get_direction()
            if direc:
                self._move(direc)
            else:
                break
        self._process_paths()
        if self.best_label is None:
            raise Exception("No resource feasible path has been found")

    def run_parallel(self):
        """
        Calculate shortest path with resource constraints.
        """
        self._init_parallel()
        p1 = Process(target=self.fwd_search.run_parallel,
                     args=(self.max_res, self.results))
        p2 = Process(target=self.bwd_search.run_parallel,
                     args=(self.min_res, self.results))
        p1.start()
        p2.start()
        p1.join(self.time_limit)
        p2.join(self.time_limit)
        self.best_labels = self.results

        self._process_paths()

    def name_algorithm(self):
        """
        Determine which algorithm is running.
        Logs algorithm classification at INFO level.
        """
        HF, HB = self.max_res[0], self.min_res[0]
        if self.direction == "forward":
            log.info("Monodirectional forward labeling algorithm")
        elif self.direction == "backward":
            log.info("Monodirectional backward labeling algorithm")
        elif HF > HB:
            log.info("Bidirectional labeling algorithm with" +
                     " dynamic halfway point")
        else:
            log.info("The algorithm can't move in either direction!")

    # Parallel private methods #

    def _init_parallel(self):
        mgr = Manager()
        self.max_res = mgr.list(self.max_res)
        self.min_res = mgr.list(self.min_res)
        self.results = mgr.dict()

    # Standard Search private methods #

    def _update_current_labels(self):
        self.current_label["forward"] = self.fwd_search.get_current_label()
        self.current_label["backward"] = self.bwd_search.get_current_label()

    def _update_res(self):
        self.min_res = self.fwd_search.get_res()
        self.max_res = self.bwd_search.get_res()

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

    def _update_best_labels(self):
        self.best_labels["forward"] = self.fwd_search.get_best_labels()
        self.best_labels["backward"] = self.bwd_search.get_best_labels()

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
                self.final_label = bwd_final

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
                    return ("forward" if len(self.unprocessed_labels["forward"])
                            < len(self.unprocessed_labels["backward"]) else
                            "backward")
            else:  # if both are empty
                return
        else:
            if (not self.current_label["forward"] and
                    not self.current_label["backward"]):
                return
            elif not self.current_label[self.direction]:
                return
            else:
                return self.direction

    ###################
    # PATH PROCESSING #
    ###################
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

    def _process_bwd_label(self, label, cumulative_res, invert_min_res=False):
        # Reverse backward path and inverts resource consumption
        label.path.reverse()
        label.res[0] = self.max_res_in[0] - label.res[0]
        if invert_min_res:
            label.res[1:] = label.res[1:] - self.min_res_in[1:]
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
        if not self.best_label or label.full_dominance(self.best_label,
                                                       "forward"):
            log.debug("Saving label {} as best".format(label))
            log.debug("With path {}".format(label.path))
            self.best_label = label
