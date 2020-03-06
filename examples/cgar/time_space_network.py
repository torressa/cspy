import copy
import logging
import numpy as np
from networkx import DiGraph, has_path, astar_path, NetworkXNoPath
# Local imports
from examples.cgar.classes import Expand, Flight
from examples.cgar.constants import OPERATING_COSTS

log = logging.getLogger(__name__)


class TSN(object):
    """
    Time-Space-Network Object with generator and updater functions.

    Parameters
    ----------
    flights : list,
        list of :class:`classes.Flight` objects
    """

    def __init__(self, flights):
        self.flights = flights
        self.last_arr = max([f.arrival for f in flights])  # last arrival
        self.data = Expand()
        self.G = DiGraph(directed=True, n_res=8)
        # Init update params
        self.it = None
        self.k_make = None
        self.airline = None
        self.duals = None
        self.first_flight = None

    def _build(self):
        self._build_data()
        self._build_graph()
        return self

    def _build_data(self):
        airports_dep = [f.origin for f in self.flights]
        airports_arrival = [f.destination for f in self.flights]
        self.data.airports = list(set(airports_arrival + airports_dep))
        self.data.airports.sort()

    def _build_graph(self):
        # Construct an Activity-on-Arc network using flights as activities
        flights = self.flights
        airports = self.data.airports

        self.G.add_node('Source',
                        pos=(-1, len(airports) + 1),
                        i_d=-1,
                        airport='Source')
        self.G.add_node('Sink',
                        pos=(self.last_arr + 1, -2),
                        i_d=-1,
                        airport='Sink')
        list(map(self._init_graph, flights))
        self._add_edges()
        log.info("Generated TSN with {} edges {} nodes".format(
            len(self.G.edges()), len(self.G.nodes())))
        # plot_graph(self.G)

    def _init_graph(self, f):
        """ Populate graph using flights from csv file"""
        label_dep = "{}_{}".format(f.origin, f.departure)  # label
        # Arrival node label
        label_arr = "{}_{}".format(f.destination, f.arrival)  # label
        self._init_node(f, label_dep, label_arr)  # Init nodes
        self._init_edge(f, label_dep, label_arr)  # Init edges

    def _init_node(self, f, label_dep, label_arr):
        # Add a Departure Node
        self.G.add_node(label_dep,
                        pos=(f.departure, self.data.airports.index(f.origin)),
                        airport=f.origin)
        # Add an Arrival Node
        self.G.add_node(label_arr,
                        pos=(f.arrival,
                             self.data.airports.index(f.destination)),
                        airport=f.destination)

    def _init_edge(self, f, label_dep, label_arr):
        # Add all flight edges
        self.G.add_edge(label_dep, label_arr, data=f._full_dict(), weight=0)
        #  Add edge from Source to departure and arrival nodes
        data_source = {
            'origin': 'Source',
            'destination': f.origin,
            'departure': -1,
            'arrival': f.departure,
            'type': f._classify_flight(0, f.departure)
        }
        self.G.add_edge('Source',
                        label_dep,
                        data=data_source,
                        weight=self._edge_weight('Source', label_dep))
        # Add edge from arrival to Sink
        data_sink = {
            'origin': f.destination,
            'destination': 'Sink',
            'departure': f.arrival,
            'arrival': self.last_arr,
            'type': f._classify_flight(f.arrival, self.last_arr)
        }
        self.G.add_edge(label_arr,
                        'Sink',
                        data=data_sink,
                        weight=self._edge_weight(label_arr, 'Sink'))

    def _add_edges(self):
        # Add edges if not already exist with their respective data
        self._add_ground_edges()
        self._add_remaining_edges()

    def _add_ground_edges(self):
        nodes = sorted(list(node for node in self.G.nodes(data=True)
                            if node[0] not in ["Source", "Sink"]),
                       key=lambda x: x[1]['pos'][0])
        for n in nodes:
            # first element in tuple has string 'Airport_time'
            # Second element in tuple has node data
            n_name, n_data = n[0], n[1]
            n_time = float(n_name.split('_')[1])
            ground_nodes_n = sorted(
                list(k for k in nodes if float(k[0].split('_')[1]) > n_time and
                     n_data['airport'] == k[1]['airport']),
                key=lambda x: x[1]['pos'][0])
            # ground_nodes_n.sort()
            if ground_nodes_n:
                m = ground_nodes_n[0]
                # for m in ground_nodes_n:
                path = None
                m_name, m_data = m[0], m[1]
                m_time = float(m_name.split('_')[1])
                if not self.G.has_edge(*(n_name, m_name)):
                    try:
                        path = astar_path(self.G, n_name, m_name)
                    except NetworkXNoPath:
                        self._add_edge(n_name, n_data, n_time, m_name, m_data,
                                       m_time)
                    if path and not all(
                            p.split('_')[0] == n_data['airport'] for p in path):
                        # if edge doesn't exist, add it
                        self._add_edge(n_name, n_data, n_time, m_name, m_data,
                                       m_time)

    def _add_remaining_edges(self):
        nodes = sorted(list(node for node in self.G.nodes(data=True)
                            if node[0] not in ["Source", "Sink"]),
                       key=lambda x: x[1]['pos'][0])
        for n in nodes:
            # first element in tuple has string 'Airport_time'
            # Second element in tuple has node data
            n_name, n_data = n[0], n[1]
            n_time = float(n_name.split('_')[1])
            nodes_n = sorted(list(
                k for k in nodes if float(k[0].split('_')[1]) > n_time),
                             key=lambda x: x[1]['pos'][0])
            # nodes_n.sort()
            for m in nodes_n:
                m_name, m_data = m[0], m[1]
                m_time = float(m_name.split('_')[1])
                if (not has_path(self.G, n_name, m_name)):
                    # if path doesn't exist add edge
                    f = list(
                        f for f in self.flights
                        if (f.origin == n_name and f.destination == m_name and
                            f.arrival - f.departure == n_time -
                            m_time and f.arrival < n_time))
                    if f:
                        self._add_edge(n_name, n_data, n_time, m_name, m_data,
                                       m_time)

    def _add_edge(self, n_name, n_data, n_time, m_name, m_data, m_time):
        data = {
            'origin': n_data['airport'],
            'destination': m_data['airport'],
            'departure': n_time,
            'arrival': m_time,
            'type': Flight._classify_flight(n_time, m_time)
        }
        self.G.add_edge(n_name,
                        m_name,
                        data=data,
                        weight=self._edge_weight(n_name, m_name,
                                                 {'data': data}))

    ################
    # Updating TSN #
    ################
    def _update_TSN(self, G, it, k_type, k_make, airline, duals, first_flight,
                    drop_edges):
        """
        Updates TSN network and returns preprocessed version,
        with less edges
        """
        edges = G.edges(data=True)
        self.it = it
        self.k_make = k_make
        self.airline = airline
        self.duals = duals
        self.first_flight = first_flight

        list(map(self._update_edge_attrs, edges))
        if drop_edges:
            return self._drop_edges(G, k_type)
        else:
            return G

    @staticmethod
    def _drop_edges(G, k_type):
        """
        Creates a copy of the TSN graph and removes
        unnecessary (Source, *) edges.
        """
        G = copy.deepcopy(G)
        count, edges = 0, G.edges(data=True)
        number_edges = len(edges)
        edges_to_remove = []
        for edge in edges:
            edge_data = edge[2]
            i_airport = edge[0].split('_')[0]
            j_airport = edge[1].split('_')[0]
            if (((k_type == 1 and edge_data['data']['type'] > k_type) or
                 (k_type == 2 and edge_data['data']['type'] != k_type)) and
                    i_airport != j_airport):
                if i_airport == 'Source' or j_airport == 'Sink':
                    pass
                else:
                    edges_to_remove.append(edge[0:2])
                    count += 1
        G.remove_edges_from(edges_to_remove)
        log.info('Removed {}/{} edges.'.format(count, number_edges))
        return G

    def _edge_weight(self, i, j, edge_data={}):
        """
        Weight function for edge between two pair of nodes.

        Parameters
        ----------
        i : string,
            tail node in the form 'LETTER_INTEGER'

        j : string,
            head node in the form 'LETTER_INTEGER'

        Returns
        -------
        int
            value with appropriate weight
        """
        if i == 'Source':
            return 0  # float(j.split('_')[1])
        elif j == 'Sink':
            return 0  # (self.last_arr - float(i.split('_')[1]))
        else:
            i_airport, i_time = i.split('_')
            j_airport, j_time = j.split('_')
            i_time, j_time = float(i_time), float(j_time)
            # if i_airport == j_airport:
            #     return (j_time - i_time)
            # else:
            if self.k_make:
                try:  # SCHEDULED CONNECTION
                    flight_dual = list(
                        w[0]
                        for w in self.duals
                        if w[1]._full_dict() == edge_data['data'])[0]
                    cost = (OPERATING_COSTS[self.k_make]['standard']
                            if i_airport != j_airport else 0)
                    return cost * (j_time - i_time) - flight_dual
                except IndexError:  # NON-SCHEDULED CONNECTION
                    cost_delay, delay = 0, 0
                    if i_airport != j_airport:
                        closest_flight = self._get_flight_copy(
                            self.flights, edge_data)
                        delay = (edge_data['data']['departure'] -
                                 closest_flight.departure)
                        flight_dual = list(w[0]
                                           for w in self.duals
                                           if w[1]._full_dict() ==
                                           closest_flight._full_dict())[0]
                        cost = OPERATING_COSTS[self.k_make]['standard']
                        cost_delay = OPERATING_COSTS[self.k_make]['copy']
                        return (cost * (j_time - i_time) + cost_delay * delay -
                                flight_dual)
                    else:
                        return (OPERATING_COSTS[self.k_make]['ground'] *
                                (j_time - i_time))
            else:
                return 0

    @staticmethod
    def _get_flight_copy(flights, edge_data):
        previous_flights = list(f for f in flights if (
            f._full_dict()['origin'] == edge_data['data']['origin'] and
            f._full_dict()['destination'] == edge_data['data']['destination']
            and f._full_dict()['departure'] < edge_data['data']['departure']))
        if previous_flights:
            return max(previous_flights, key=lambda x: x.departure)
        else:
            return

    def _update_edge_attrs(self, edge):
        """
        Update edge attributes using dual values from the solution of the
        relaxed master problem.

        Parameters
        ----------
        edge : edge
            edge to update.

        it : int
            iteration number.

        duals : list of tuples
            (dual, classes.Flight). dual values from the master problem
            and schedule.

        first_flight : object, :class:`classes.Flight`
            first flight scheduled.
        """

        def __update_weight(edge):
            edge_data = edge[2]
            weight = self._edge_weight(*edge)
            edge_data['weight'] = weight

        def __update_res_cost(edge):
            edge[2]['res_cost'] = np.zeros(self.G.graph['n_res'])

        __update_weight(edge)
        __update_res_cost(edge)
