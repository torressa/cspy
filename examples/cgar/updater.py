from examples.cgar.classes import Schedule


def update(k, it, path, Data, Master, stop=False):
    """
    Generate column for the master problem using shortest path and
    updates the data with new combination of flights for a certain aircraft

    Parameters
    ----------
    k : string
        aircraft
    it : int
        iteration numbe
    path : list
        f tuples, edges in shortest path solution.
                    1st element is the edge data dictionary, 2nd is the weight
    Data : object
        classes.Data; data to update
    MasterObj object
        master.Master; master problem

    :return:
    master : object
        gurobipy.Model; master problem with new column
    data : object
        classes.Data; updated data object
    stop : bool
        indicating if reduced cost is positive
    """

    def _update_data():
        schedule = Schedule()
        schedule.label = (it, k, 's_%s_%s' % (it, k))
        schedule.cost = cost_col
        schedule.aircraft = k
        schedule.flights = [
            f for f in Data.flights for p in path if f._full_dict() == p[0]
        ]
        Data.scheds[schedule.label] = schedule
        return Data

    master, cost_col = Master._generate_column(k, it, path)
    Data = _update_data()
    return master, Data, cost_col
