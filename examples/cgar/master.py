import logging
from pulp import (LpProblem, LpConstraintVar, LpVariable, LpMinimize, lpSum,
                  LpBinary, LpContinuous, LpConstraintGE, LpConstraintLE)
from cgar.classes import Expand

log = logging.getLogger(__name__)


class Master:
    """
    Master Object for initialising, solving, updating, and column creation
    of the aircraft recovery master problem
    """

    def __init__(self, Data):
        """
        Formulate the master problem.

        Parameters
        ----------
        Data : object,
            classes.Data object with problem data.
        """
        self.Data = Data
        self.master = Expand()
        # Init lp relaxation of the master problem
        self.relax = Expand()
        # Init master problem with empty constraints and objective
        self.master.model = LpProblem("master problem")
        self.master.objective = LpConstraintVar("obj")
        # Container for flight constraints
        self.master.flight_constrs = {}
        # Container for assignment constraints
        self.master.assign_constrs = {}

        self._formulate_master()

    def _formulate_master(self):
        """
        Formulate set covering formulation for aircraft recovery
        """
        # Variable dicts
        a_dict = {
            (s_label[1], s): s.cost for s_label, s in self.Data.scheds.items()
        }
        dum_dict = {
            f: 20000 + 20000 * (f.arrival - f.departure)
            for f in self.Data.flights
        }
        # CONSTRAINTS #
        # Generate empty >= constraints for all flights
        self.master.flight_constrs = {
            key: LpConstraintVar(key, LpConstraintGE, 1)
            for key in dum_dict.keys()
        }
        # Generate empty <= constraints for all aircraft
        self.master.assign_constrs = {
            k: LpConstraintVar(k, LpConstraintLE, 1) for k in self.Data.aircraft
        }
        # VARIABLES #
        # Create dummy variables for each flight
        dummy = {
            key: LpVariable(
                'dummy{0}'.format(key), 0, 1, LpBinary,
                lpSum(val * self.master.objective +
                      self.master.flight_constrs[key]))
            for key, val in dum_dict.items()
        }
        # Create assignment variables for each aircraft (and schedule)
        a = {
            key_tuple:
            LpVariable('a[{}]'.format(key_tuple), 0, 1, LpBinary,
                       lpSum(self.master.assign_constrs[key_tuple[0]]))
            for key_tuple, val in a_dict.items()
        }
        # Add flight constraints to model
        for constr in self.master.flight_constrs.values():
            self.master.model += constr
        # Add assignment constraints to the model
        for constr in self.master.assign_constrs.values():
            self.master.model += constr
        # Set objective function
        self.master.model.sense = LpMinimize
        self.master.model.setObjective(self.master.objective)
        # Print to file for debugging
        # self.master.model.writeLP("./output/init.lp")

    def _solve_relax(self):
        """
        Relaxes and solves the master problem.

        Returns
        -------
        duals : list of tuples,
            list of tuples with structure (dual value, classes.Flight)

        self.relax : attribute,
            Master attribute with relaxed version of the problem.
        """
        self.relax = self.master
        for v in self.relax.model.variables():
            v.cat = LpContinuous

        self.relax.model.solve()
        duals = [(float(self.relax.model.constraints[i].pi),
                  [f
                   for f in self.Data.flights
                   if str(f) == i][0])
                 for i in self.relax.model.constraints
                 if "Flight" in i]
        duals = sorted(duals, key=lambda x: x[1].i_d)
        return self.relax, duals

    def _generate_column(self, k, it, path):
        """
        Adds column using shortest path from extended TSN.

        Parameters
        ----------
        k : str,
            aircraft in subproblem

        it : int,
            iteration number

        path : list,
            edges in shortest path [(edge_dict, edge_weight), ..]

        Returns
        -------
        self : object,
            Updated Master object

        cost : float,
            Reduced cost of column
        """
        flights = self.Data.flights
        # count number of dummy edges for column obj coeff
        cost_col = 0
        flights_in_path = []

        for p in path:  # for each flight in the path
            if any(f._full_dict() == p[0] for f in flights):
                flight = [f for f in flights if f._full_dict() == p[0]][0]
                # Get constraints associated with flight
                flights_in_path.append(flight)
            else:
                cost_col += p[1]
        # Get aircraft dual
        lambda_k = [
            float(self.relax.model.constraints[i].pi)
            for i in self.relax.model.constraints
            if i == k.replace("-", "_")
        ][0]
        # cost of path + 2 due to first edge initialisation
        cost = 2 + sum([p[1] for p in path]) - lambda_k
        if cost < 0:
            # Add variable to master problem in appropriate columns
            var = LpVariable(
                'a({}, s_{}_{})'.format(k, it, k), 0, 1, LpBinary,
                lpSum(self.master.flight_constrs[f] for f in flights_in_path) +
                lpSum(self.master.assign_constrs[k]))
            self.master.model.objective += lpSum(cost_col * var)
        # Print to file for debugging
        # self.master.model.writeLP("./output/iteration_{}.lp".format(it))
        return self, cost
