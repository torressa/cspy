from __future__ import absolute_import, print_function

import logging

from numpy import array
from numpy.random import RandomState
from networkx import relabel_nodes, set_edge_attributes

WALKING_SPEED = 3  # km per hour


def relabel_source_sink(G):
    """
    Identify and relabel source and sink nodes
    """
    # Identify Source and Sink according to specifications
    # Source is the post office in Ternatestraat
    source = list(e for e in G.edges(data=True)
                  if 'name' in e[2] and 'Ternatestraat' in e[2]['name'])[-2][0]
    # Sink is Jane's home in Ceramstraat
    sink = list(e for e in G.edges(data=True)
                if 'name' in e[2] and 'Delftweg' in e[2]['name'])[0][1]
    # Relabel nodes
    G = relabel_nodes(G, {source: 'Source', sink: 'Sink'})
    return G


def add_cspy_edge_attributes(G, seed=None):
    """
    Set edge attributes required for cspy
    """
    if seed is None:
        random_state = RandomState()
    elif isinstance(seed, int):
        random_state = RandomState(seed)
    elif isinstance(seed, RandomState):
        random_state = seed
    else:
        raise Exception(
            '{} cannot be used to seed numpy.random.RandomState'.format(seed))
    # Initialise edge attributes
    set_edge_attributes(G, 0, 'weight')
    set_edge_attributes(G, 0, 'res_cost')
    # Iterate through edges to specify 'weight' and 'res_cost' attributes
    for edge in G.edges(data=True):
        # Distance is converted from an already existing edge attribute (m to km)
        dist = edge[2]['length'] * 0.001
        # Fixed resource costs for a given edge.
        # 'sights' is a random integer between [0, 5)
        res_cost_sights = random_state.randint(1, 5)
        # 'travel-time' is distance over speed (not necessary)
        res_cost_travel_time = dist / float(WALKING_SPEED)
        # 'delivery time' is a random number between the travel-time for
        # the edge and 10 times the travel time.
        # in reality this would depend on the buildings present
        res_cost_delivery_time = random_state.uniform(res_cost_travel_time,
                                                      10 * res_cost_travel_time)
        # 'shift' is not required.
        res_cost_shift = 0

        edge[2]['res_cost'] = array([
            0, res_cost_sights, res_cost_shift, res_cost_travel_time,
            res_cost_delivery_time
        ])
        edge[2]['weight'] = 0  #-dist
    return G
