import os
import logging
from pandas import read_csv
from classes import Flight
from time_space_network import TSN

log = logging.getLogger(__name__)


def load_df(airline):
    ''' Loads csv file using pandas
    RETURNS
        csv :: object, pandas.DataFrame'''
    work_dir = './input/'
    prefixed = [
        filename for filename in os.listdir(work_dir)
        if filename.startswith(airline)
    ][0]
    df = read_csv(work_dir + prefixed)
    return df


def get_aircraft(csv):
    ''' Loads aircraft list and removes duplicates
    INPUTS
        csv :: object, pandas.DataFrame
    RETURNS
        aircraft :: list, list of strings with aircraft ids'''
    aircraft = list(set(csv['aircraft']))
    return aircraft


def get_flights(df):
    ''' Generates a list of Flight objects from the csv file to then
    populate the TSN network.
    INPUTS
        df :: object, pandas.DataFrame
    RETURNS
        flights    :: list of classes.Flight objects;
        TSN_object :: object, classes.TSN; initial TSN'''

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
    ground = list(
        f._instance_from(f.destination, f_n.origin, f.arrival, f_n.departure)
        for k in aircraft_list
        for f, f_n in zip(
            sorted([f for f in flights if f.aircraft.tail == k],
                   key=lambda x: x.departure),
            sorted([f for f in flights if f.aircraft.tail == k],
                   key=lambda x: x.departure)[1:])
        if f.arrival < f_n.departure)
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
    ''' Generates a list of Schedule objects with the appropriate attributes
    INPUTS
        aircraft_list :: list, aircrafts in plan
        flights       :: list of classes.Flight objects
    OUTPUTS
        schedules     :: list of classes.Schedule objects'''
    from classes import Schedule
    schedules = {}
    # logging.info('[%s] Initial flight assignment' % __name__)
    for k in aircraft_list:
        schedule = Schedule()
        schedule.label = (0, k, 's_0_%s' % k)
        schedule.flights = [f for f in flights if f.aircraft.tail == k]
        schedule.cost = 10000
        schedule.aircraft = k
        schedules[schedule.label] = schedule
        # logging.info("    %s %s" % (k, schedule.flights))
    return schedules


def preprocess(df):
    '''Gathers all information in a Data object.
    INPUTS
        csv :: object, pandas.DataFrame
    RETURNS
        data :: object, classes.Data'''
    from classes import Data
    data = Data()
    data.aircraft = get_aircraft(df)
    data.flights = get_flights(df)
    data.flights, data.graph, data.flight_count = get_ground_connections(
        data.aircraft, data.flights)
    data.scheds = get_scheds(data.aircraft, data.flights)
    return data


def read_input(airline):
    df = load_df(airline)
    data = preprocess(df)
    return data
