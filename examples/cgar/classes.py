class Expand(object):
    pass


class Data(object):
    """
    INPUT
        fields  :: dictionary with field names
    """
    _FIELDS = {
        'scheds': {},
        'aircraft': [],
        'flights': [],
        'graph': None,
        'flight_count': 0
    }

    def __init__(self, fields=_FIELDS):

        self.scheds = fields.get('scheds')
        self.aircraft = fields.get('aircraft')
        self.flights = fields.get('flights')
        self.graph = fields.get('graph')
        self.flight_count = fields.get('flight_count')

    def __repr__(self):  # for printing w/o print function.
        return str(self)

    def __str__(self):  # for printing purposes
        return "DataObj"


class Schedule(object):
    """
    INPUT
        fields  :: dictionary with field names
    """
    _FIELDS = {'label': None, 'cost': [], 'flights': [], 'aircraft': []}

    def __init__(self, fields=_FIELDS):
        self.label = fields.get('label')
        self.cost = fields.get('cost')
        self.flights = fields.get('flights')
        self.aircraft = fields.get('aircraft')

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "ScheduleObj(%s)" % self.label[2]


class Flight(object):
    """
    Simple Flight object.

    Parameters
    ----------
    i_d : int,
        flight identifier.
    cost : int,
        cost to perform flight
    aircraft : string,
        aircraft assigned to flight
    origin : string,
        origin airport
    destination string,
        destination airport
    departure : int,
        time of departure (UNIX timestamp)
    arrival : int,
        time of arrival (UNIX timestamp)
    """

    def __init__(self, i_d, cost, aircraft, plane_type, origin, destination,
                 departure, arrival):
        self.i_d = i_d
        self.cost = cost
        self.aircraft = Expand()
        self.aircraft.tail = aircraft
        self.aircraft.type = plane_type
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.type = self._classify_flight(departure, arrival)

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "FlightObj({})".format(self.i_d)

    def _full_dict(self):
        '''Returns dictionary with attribute information'''
        return {
            'origin': self.origin,
            'destination': self.destination,
            'departure': self.departure,
            'arrival': self.arrival,
            'type': self.type
        }

    def _instance_from(self, origin, destination, departure, arrival):
        return Flight(self.i_d, self.cost, self.aircraft.tail,
                      self.aircraft.type, origin, destination, departure,
                      arrival)

    @staticmethod
    def _classify_flight(departure, arrival):
        ''' Function to classify a flight according to its length/duration.'''
        flight_time = (arrival - departure)
        if flight_time <= 3:
            return 0  # 'Short-haul'
        elif 3 < flight_time < 6:
            return 1  # 'Medium-haul'
        elif flight_time >= 6:
            return 2  # 'Long-haul'

    @staticmethod
    def _classify_aircraft(aircraft):
        '''Function to classify a aircraft according to its type and range.'''
        if aircraft == 'JS32' or aircraft == 'DH8D':
            return 0  # short-haul
        elif (aircraft == 'A320' or aircraft == 'A321' or aircraft == 'A319' or
              aircraft == 'B738' or aircraft == 'B752'):
            return 1  # Medium-haul
        elif aircraft == 'B77L' or aircraft == 'A359':
            return 2  # Long-Haul
        else:
            return
