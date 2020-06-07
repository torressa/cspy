import logging
from pulp import value
# Local imports
from examples.cgar.master import Master
from examples.cgar.sub import Subproblem
from examples.cgar.updater import update

log = logging.getLogger(__name__)


def algorithm(Data, n_runs, airline):
    """
    Runs column generation algorithm where each subproblem is a
    shortest path problem with resource constraints.
    Stops if reduced cost of column is +ve

    Parameters
    ----------
    Data : object,
        classes.Data; initial input data

    n_runs : int,
        number of runs for the column generation algorithm

    airline : string,
        name of airline under consideration
    """

    MasterObj = Master(Data)  # formulate master problem
    relax, duals = MasterObj._solve_relax()  # solve relaxed version
    iteration, red_cost_count, col_count = 1, 0, 0  # init algorithm parameters

    red_cost_k = {k: 0 for k in Data.aircraft}
    while red_cost_count < len(Data.aircraft) and iteration < n_runs:
        for k in Data.aircraft:  # for each aircraft
            if red_cost_k[k] == 0:  # if reduced cost not positive
                # Solve corresponding subproblem
                SP = Subproblem(k, iteration, duals, Data, airline)
                shortest_path = SP._solve_cspy()
                MasterObj, _, cost = update(k, iteration, shortest_path, Data,
                                            MasterObj)
                if float(cost) < 0:
                    log.info(" Added a column with cost : {}".format(cost))
                    col_count += 1
                else:
                    log.info(" Solved and produced +ve reduced cost")
                    red_cost_k[k] += 1
                relax, duals = MasterObj._solve_relax()
                log.info(" Linear relaxation objective value : {}".format(
                    value(relax.model.objective)))
                red_cost_count = sum(min(1, val) for val in red_cost_k.values())
        iteration += 1

    MasterObj.master.model.solve()
    log.info(" Final objective value with integer variables : {}".format(
        value(MasterObj.master.model.objective)))
    return
