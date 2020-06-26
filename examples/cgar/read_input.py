import os
from logging import getLogger
from pandas import read_csv
# local imports
from examples.cgar.time_space_network import TSN
from examples.cgar.classes import Flight, Data, Schedule

log = getLogger(__name__)


def load_df(airline):
    """
    Loads csv file using pandas

    Returns
    -------
    csv : object,
        pandas.DataFrame
    """
    work_dir = 'examples/cgar/input/'
    # Working directory with respect to test runner.
    # i.e. if want to run tests locally from tests/,
    # this needs to be changed to '../examples/cgar/input/'
    prefixed = [
        filename for filename in os.listdir(work_dir)
        if filename.startswith(airline)
    ][0]
    return read_csv(work_dir + prefixed)


def get_aircraft(csv):
    """
    Loads aircraft list and removes duplicates

    Parameters
    ----------
    csv : object,
        pandas.DataFrame

    Returns
    -------
    aircraft : list,
        list of strings with aircraft ids
    """
    return list(set(csv['aircraft']))


def get_flights(df):
    """
    Generates a list of Flight objects from the csv file to then
    populate the TSN network.

    Parameters
    ----------
    df : object,
        pandas.DataFrame

    Returns
    -------
    flights : list,
        list of classes.Flight objects;

    TSN_object : object,
        classes.TSN; initial TSN
    """
    # Create a list of Flight objects, one per row in the df
    flights = list(
        Flight(idx, 0, row['aircraft'], row['type'], row['origin'].replace(
            ' ', ''), row['destination'].replace(' ', ''),
               float(row['departure']), float(row['arrival']))
        for idx, row in df.iterrows()
        if float(row['departure']) < float(row['arrival']))
    return flights


def get_ground_connections(aircraft_list, flights):
    """
    For each aircraft, get all current and next flights
    """
    ground = [
        f._instance_from(f.destination, f_n.origin, f.arrival, f_n.departure)
        for k in aircraft_list
        for f, f_n in zip(
            sorted(
                [f for f in flights if f.aircraft.tail == k],
                key=lambda x: x.departure,
            ),
            sorted(
                [f for f in flights if f.aircraft.tail == k],
                key=lambda x: x.departure,
            )[1:],
        )
        if f.arrival < f_n.departure
    ]

    flights = flights + ground
    flights.sort(key=lambda x: x.departure)
    # Overwrite ids
    count = 0
    for f in flights:
        f.i_d = count
        count += 1
    # Init TSN network with all connections including ground and others
    log.info(
        "Total number of flights is: {} (including ground arcs)".format(count))
    TSN_object = TSN(flights)._build()
    return flights, TSN_object, count


def get_scheds(aircraft_list, flights):
    """
    Generates a list of Schedule objects with the appropriate attributes

    Parameters
    ----------
    aircraft_list : list,
        aircrafts in plan

    flights : list,
        list of classes.Flight objects

    Returns
    -------
    schedules : list,
        list of classes.Schedule objects
    """
    schedules = {}
    for k in aircraft_list:
        schedule = Schedule()
        schedule.label = (0, k, 's_0_%s' % k)
        schedule.flights = [f for f in flights if f.aircraft.tail == k]
        schedule.cost = 10000
        schedule.aircraft = k
        schedules[schedule.label] = schedule
    return schedules


def preprocess(df):
    """
    Gathers all information in a Data object.

    Parameters
    ----------
    csv : object,
        pandas.DataFrame

    Returns
    -------
    data : object,
        classes.Data
    """
    data = Data()
    data.aircraft = get_aircraft(df)
    data.flights = get_flights(df)
    data.flights, data.graph, data.flight_count = get_ground_connections(
        data.aircraft, data.flights)
    data.scheds = get_scheds(data.aircraft, data.flights)
    return data


def read_input(airline):
    df = load_df(airline)
    return preprocess(df)
