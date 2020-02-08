import logging
# Local imports
from master import Master
from sub import Subproblem
from updater import update

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

    Returns
    -------
    master_mdl : object,
        gurobipy.Model; final master model with all columns and final solution

    data : object,
        classes.Data; updated data
    """

    MasterObj = Master(Data)  # formulate master problem
    relax, duals = MasterObj._solve_relax()  # solve relaxed version
    iteration, red_cost_count, col_count = 1, 0, 0  # init parameters

    red_cost_k = {k: 0 for k in Data.aircraft}
    while red_cost_count < len(Data.aircraft) and iteration < n_runs:
        for k in Data.aircraft:  # for each aircraft
            if red_cost_k[k] == 0:  # if reduced cost not positive
                # Solve corresponding subproblem
                SP = Subproblem(k, iteration, duals, Data, airline)
                shortest_path = SP._solve_cspy()
                MasterObj, data, cost = update(k, iteration, shortest_path,
                                               Data, MasterObj)
                if float(cost) < 0:
                    log.info(" Added a column with cost : {}".format(cost))
                    col_count += 1
                elif float(cost) >= 0:
                    log.info(" Solved and produced +ve reduced cost")
                    red_cost_k[k] += 1
                relax, duals = MasterObj._solve_relax()
                log.info(" Linear relaxation objective value : {}".format(
                    relax.objVal))
                red_cost_count = sum(
                    [min(1, val) for val in red_cost_k.values()])
        iteration += 1

    MasterObj.master.optimize()
    log.info(" Final objective value with integer variables : {}".format(
        MasterObj.master.objVal))
    return MasterObj.master, data
