import logging
from gurobipy import Model, Column

log = logging.getLogger(__name__)


class Master:
    """ Master Object for initialising, solving, updating, and column creation
     of the tail assignment master problem"""

    def __init__(self, Data):
        """Formulate the master problem.
        INPUTS
            Data    :: object, classes.Data; problem data.
        """
        self.Data = Data
        self.duals = []
        self.master = Model("master LP")  # Init master model
        self.master.Params.OutputFlag = 0  # No output

        self._formulate_master()

    def _formulate_master(self):
        """ Formulate set partitioning model for tail assignment"""
        # Variable dicts #
        a_dict = {
            (s_label[1], s): s.cost for s_label, s in self.Data.scheds.items()
        }
        dum_dict = {
            f: 20000 + 20000 * (f.arrival - f.departure)
            for f in self.Data.flights
        }
        # VARIABLES #
        a = self.master.addVars(a_dict.keys(), name="a", vtype="B")
        dummy = self.master.addVars(dum_dict.keys(), name="dummy", vtype="B")
        # OBJECTIVE FUNCTION #
        self.master.setObjective(dummy.prod(dum_dict))
        # FLIGHT CONSTRAINTS #
        self.master.addConstrs((dummy[key] >= 1 for key in dum_dict.keys()),
                               name='flight')
        # AIRCRAFT CONSTRAINTS #
        self.master.addConstrs((a.sum(k, '*') <= 1 for k in self.Data.aircraft),
                               name='aircraft_schedule')
        self.master.update()
        # write to file
        self.master.write("./output/init.lp")

    def _solve_relax(self):
        """
        Relaxes and solves the master problem.
        INPUTS
            master  :: object, gurobipy.Model; master problem.
        RETURNS
            duals   :: list of tuples, (dual, classes.Flight)
            relax   :: object, gurobipy.Model; relaxed master problem.
        """
        self.relax = self.master.relax()
        self.relax.update()
        self.relax.optimize()
        duals = [(float(c.Pi), [
            f for f in self.Data.flights if f.i_d == self._split(c.ConstrName)
        ][0]) for c in self.relax.getConstrs() if "flight" in c.ConstrName]
        duals = sorted(duals, key=lambda x: x[1].i_d)
        self.duals.append([d[0] for d in duals])
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
        master : object,
            gurobipy.Model; updated master problem with new column
        """

        col = Column()  # Init Column
        flights = self.Data.flights
        cost_col = 0  # count number of dummy edges for column obj coeff

        for p in path:  # for each flight in the path
            if any(f._full_dict() == p[0] for f in flights):
                flight = [f for f in flights if f._full_dict() == p[0]][0]
                # Get constraints associated with flight
                constrs = [
                    c for c in self.master.getConstrs()
                    if "flight" in c.ConstrName and
                    self._split(c.ConstrName) == flight.i_d
                ]
                # Add terms to column for each constraint
                col.addTerms([1] * len(constrs), constrs)
            else:
                cost_col += p[1]
        # Get constraints associated with aircraft k
        constr = [
            c for c in self.master.getConstrs()
            if "aircraft_schedule" in c.ConstrName and k in c.ConstrName
        ][0]
        col.addTerms(1, constr)
        # Get aircraft dual for cost
        lambda_k = [
            float(c.Pi)
            for c in self.relax.getConstrs()
            if "aircraft_schedule" in c.ConstrName and k in c.ConstrName
        ][0]
        # cost of path + 2 due to first edge initialisation
        cost = 2 + sum([p[1] for p in path]) - lambda_k
        if cost < 0:
            self.master.addVar(obj=cost_col,
                               vtype="B",
                               name="a[%s,s_%s_%s]" % (k, it, k),
                               column=col)
            self.master.update()
        return self, cost

    @staticmethod
    def _split(string):
        """ Split integers in string and return last occurrence"""
        import re
        return list(map(int, re.findall(r'\d+', string)))[-1]