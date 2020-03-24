import sys
from abc import ABCMeta
from copy import deepcopy
from logging import getLogger

from numpy import array

# Local imports
from examples.cgar.classes import Flight
from examples.cgar.constants import (AIRLINES_DATA, CREW_COST, CREW_REST,
                                     MAX_CREWD1, MAX_CREWD2, MIN_MAINT,
                                     PENALTY)
from examples.cgar.time_space_network import TSN

sys.path.append("../../cspy")

from cspy.algorithms.bidirectional import BiDirectional

log = getLogger(__name__)


class Subproblem:
    """
    Subproblem class. Solves the shortest path problem with resource
    constraints on a TSN (with appropriate weights) using the cspy module.

    Parameters
    ----------
    k : string,
        aircraft tail number;

    it : int,
        iteration number;

    master_relax : object :class:`gurobipy.Model()`;
        relaxed master problem;

    Data : object :class:`Data`
        object with schedule data, flight data, and generated TSN.

    airline : str, optional
        airline under consideration.

    Returns
    -------
    flight_path : list,
        tuples with edge data dictionary and weight. Edges in shortest path.
    """

    __metaclass__ = ABCMeta

    def __init__(self, k, it, duals, Data, airline=None):
        self.k = k
        self.it = it
        self.duals = duals
        self.Data = Data
        self.airline = airline
        # Get first flight for aircraft
        self.first_flight, self.max_FH = self._get_first_flight()
        # Classify aircraft
        self.k_type = Flight._classify_aircraft(
            self.first_flight.aircraft.type)
        self.k_make = self.first_flight.aircraft.type
        self._get_flight_copy = TSN._get_flight_copy

        TSNObj = Data.graph
        G = deepcopy(TSNObj.G)
        self.G_pre = TSNObj._update_TSN(G, self.it, self.k_type, self.k_make,
                                        self.airline, self.duals,
                                        self.first_flight, False)

    def _get_first_flight(self):
        sched_k = list(sched for key, sched in self.Data.scheds.items()
                       if sched.label[2] == 's_{}_{}'.format(0, self.k))[0]
        sorted_flights = sorted([f for f in sched_k.flights],
                                key=lambda x: x.departure)
        max_FH = sum(f.arrival - f.departure for f in sorted_flights)
        return sorted_flights[0], max_FH

    def _solve_cspy(self):
        # Solve subproblem with exact algorithm
        log.info(" Solving subproblem for aircraft {}".format(self.k))
        G = deepcopy(self.G_pre)
        n_edges = len(G.edges())
        crew_ub = AIRLINES_DATA[self.airline]['crew_budget']
        max_res = [
            n_edges, 0.0, self.max_FH, crew_ub, MAX_CREWD1, MAX_CREWD2, 0.0,
            1.0
        ]
        min_res = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        bidirec = BiDirectional(G,
                                max_res,
                                min_res,
                                direction='both',
                                preprocess=True,
                                REF_forward=self.REF,
                                REF_backward=self.REF_backward)
        bidirec.run()
        path = bidirec.path
        self.shortest_path = [(edge[2]['data'], edge[2]['weight'])
                              for edge in G.edges(data=True)
                              if edge[0:2] in zip(path, path[1:])]
        return self.shortest_path

    def REF(self, res, edge):
        """
        Custom resource extension function that uses a cumulative resource
        vector `res` and the extension through `edge` to update the
        cumulative resource vector.
        """
        def _check_hub(airport, airline):
            return any(base in airport
                       for base in AIRLINES_DATA[airline]['hub'])

        def _check_flight(flight, penalty=False):
            """
            Updates cumulative resources according to REF rules

            Returns
            -------
            array
                updated array of cumulative resources
            """
            # unpack cumulative resources
            mono, air, maint, crewb, crewd1, crewd2, pasg, dead = arr
            mono += 1  # monotone
            air, pasg = 0, 0  # aircraft type, passenger delay
            duration = (flight.arrival - flight.departure)

            # PASSENGERS
            if penalty:  # if dummy flight
                closest_flight = self._get_flight_copy(self.Data.flights,
                                                       edge_data)
                # Find original flight
                if closest_flight and ((closest_flight.type == 0
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure >= 2) or
                                       (closest_flight.type == 1
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure >= 3) or
                                       (closest_flight.type == 2
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure) >= 4):
                    # If delay wrt original flight exceeds regulations
                    pasg = 1

            # REST OF RESOURCES
            if flight.origin == flight.destination:
                # Ground connection
                if _check_hub(flight.destination, self.airline):
                    # Ground connection at HUB
                    crewd1 = 0  # crew duty 1 reset
                    if flight.arrival - flight.departure >= MIN_MAINT:
                        maint = 0  # maintenance reset
                else:
                    # Ground connection not at HUB
                    crewb += CREW_COST['wait'] * duration
                if flight.arrival - flight.departure >= CREW_REST:
                    # if enough rest for crew
                    crewd2 = 0  # crew duty 2 reset regardless of airport
            else:
                # Flight (deadhead or not)
                if ((self.k_type == 1 and flight.type > self.k_type)
                        or ((self.k_type == 2 or self.k_type == 0)
                            and flight.type != self.k_type)):
                    # If flight doesn't match aircraft type
                    air = 1
                maint += duration  # maintenance
                crew_cost = CREW_COST[
                    self.k_type] + PENALTY if penalty else CREW_COST[
                        self.k_type]
                crewb += crew_cost * duration  # crew budget
                crewd1 += duration  # crew duty rule 1
                crewd2 += duration  # crew duty rule 2
            # DEADHEAD RESOURCE
            if edge_data['weight'] > 0:
                dead += -1  # Deadhead flight
            else:
                dead = 1  # Scheduled flight
            return array([mono, air, maint, crewb, crewd1, crewd2, pasg, dead])

        i, j, edge_data = edge[0], edge[1], edge[2]
        arr = array(res)
        # [monotone, air, maint, crewb, crewd1, crewd2, pass, dead]
        if i == 'Source' or j == 'Sink':
            arr[-1] = 1  # deadhead flights
        else:
            data = edge_data['data']
            if any(f._full_dict() == data for f in self.Data.flights):
                # SCHEDULED FLIGHT
                f = [f for f in self.Data.flights if f._full_dict() == data][0]
                arr = _check_flight(f)
            else:
                # UNSCHEDULED FLIGHT
                i_airport, i_time = i.split('_')
                j_airport, j_time = j.split('_')
                i_time, j_time = float(i_time), float(j_time)
                # Retrieve potential flight
                dummy_list = list(
                    f for f in self.Data.flights
                    if f.origin == i_airport and f.destination == j_airport
                    and f.departure - f.arrival == j_time - i_time)
                if dummy_list:
                    dummy_f = dummy_list[0]
                else:
                    dummy_f = Flight(0, 0, self.k, self.k_type, i_airport,
                                     j_airport, i_time, j_time)
                arr = _check_flight(dummy_f, True)
        return arr

    def REF_backward(self, res, edge):
        """
        [Backward] Custom resource extension function that uses a
        cumulative resource vector ``res`` and the extension through
        ``edge`` to update the cumulative resource vector.
        """
        def _check_hub(airport, airline):
            return any(base in airport
                       for base in AIRLINES_DATA[airline]['hub'])

        def _check_flight(flight, penalty=False):
            """
            Updates cumulative resources according to REF rules

            Returns
            -------
            array
                updated array of cumulative resources
            """
            # unpack cumulative resources
            mono, air, maint, crewb, crewd1, crewd2, pasg, dead = arr
            mono -= 1  # monotone
            air, pasg = 0, 0  # aircraft type, passenger delay
            duration = (flight.arrival - flight.departure)

            # PASSENGERS
            if penalty:  # if dummy flight
                closest_flight = self._get_flight_copy(self.Data.flights,
                                                       edge_data)
                # Find original flight
                if closest_flight and ((closest_flight.type == 0
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure >= 2) or
                                       (closest_flight.type == 1
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure >= 3) or
                                       (closest_flight.type == 2
                                        and edge_data['data']['departure'] -
                                        closest_flight.departure) >= 4):
                    # If delay wrt original flight exceeds regulations
                    pasg = 1

            # REST OF RESOURCES (except deadhead)
            if flight.origin == flight.destination:
                # Ground connection
                if _check_hub(flight.destination, self.airline):
                    # Ground connection at HUB
                    crewd1 = MAX_CREWD1  # crew duty 1 reset
                    if flight.arrival - flight.departure >= MIN_MAINT:
                        maint = self.max_FH  # maintenance reset
                else:
                    # Ground connection at not HUB
                    crewb -= CREW_COST['wait'] * duration
                # if enough rest for crew reset regardless of airport
                if flight.arrival - flight.departure >= CREW_REST:
                    crewd2 = MAX_CREWD2  # crew duty 2 reset
            else:
                # Flight (deadhead or not)
                if ((self.k_type == 1 and flight.type > self.k_type)
                        or ((self.k_type == 2 or self.k_type == 0)
                            and flight.type != self.k_type)):
                    # If flight doesn't match aircraft type
                    air = 1
                maint += duration  # maintenance
                crew_cost = CREW_COST[
                    self.k_type] + PENALTY if penalty else CREW_COST[
                        self.k_type]
                crewb -= crew_cost * duration  # crew budget
                crewd1 -= duration  # crew duty rule 1
                crewd2 -= duration  # crew duty rule 2
            # DEADHEAD RESOURCE
            if edge_data['weight'] > 0:
                dead += -1  # Deadhead flight
            else:
                dead = 1  # Scheduled flight
            return array([mono, air, maint, crewb, crewd1, crewd2, pasg, dead])

        i, j, edge_data = edge[0], edge[1], edge[2]
        arr = array(res)
        # [monotone, air, maint, crewb, crewd1, crewd2, pass, dead]
        if i == 'Source' or j == 'Sink':
            arr[-1] = 1  # deadhead flights
        else:
            data = edge_data['data']
            if any(f._full_dict() == data for f in self.Data.flights):
                # SCHEDULED FLIGHT
                f = [f for f in self.Data.flights if f._full_dict() == data][0]
                arr = _check_flight(f)
            else:
                # UNSCHEDULED FLIGHT
                i_airport, i_time = i.split('_')
                j_airport, j_time = j.split('_')
                i_time, j_time = float(i_time), float(j_time)
                # Retrieve potential flight
                dummy_list = list(
                    f for f in self.Data.flights
                    if f.origin == i_airport and f.destination == j_airport
                    and f.departure - f.arrival == j_time - i_time)
                if dummy_list:
                    dummy_f = dummy_list[0]
                else:
                    dummy_f = Flight(0, 0, self.k, self.k_type, i_airport,
                                     j_airport, i_time, j_time)
                arr = _check_flight(dummy_f, True)
        return arr
