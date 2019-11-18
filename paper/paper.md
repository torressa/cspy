---
title: 'cspy: A Python package with a collection of algorithms for the (Resource) Constrained Shortest Path problem'
tags:
  - Python
  - Resource Constrained Shortest Path
  - Networks
  - Graph Theory
authors:
  - name: David Torres Sanchez
    orcid: 0000-0002-2894-9432
    affiliation: 1
affiliations:
 - name: STOR-i, Lancaster University, UK.
   index: 1
date: July 2019
bibliography: paper.bib
---

# Introduction

When solving the shortest path problem and considering multiple operational restrictions, one may resort to the (resource) constrained shortest path (CSP) problem.
It consists, as its name suggests, in finding, among all paths, the shortest path from source to sink nodes that satisfies a set of constraints for a defined set of resources.
Such set of resources and the way they evolve throughout the path are user defined and controlled. This allows the modelling of a wide variety of problems including: the vehicle routing problem with time windows, the technician routing and scheduling problem, the capacitated arc-routing problem, on-demand transportation systems, and, airport ground movement [@Desrochers1988; @Feillet2004; @Inrich2006; @Righini2008; @Bode2014; @Chen2016; @GARAIX201062; @Tilk2017; @Zamorano2017].

``cspy`` is a Python package that allows you to solve instances of the CSP problem using up to eight different algorithms.

``cspy`` is of interest to the operational research community and others that wish to solve an instance of the CSP problem.

# Algorithms

Even though the CSP problem is $\mathcal{NP}$-hard [@gary1979], several algorithms have been developed to solve it. The most common algorithms are dynamic programming labelling algorithms. 
@inrich presented an exact algorithm based on DP, the monodirectional forward labelling algorithm, based on the pioneering work by @Desrochers1988. 

Advanced and efficient algorithms have been developed since. @Boland2006 published a state augmenting algorithm that uses a monodirectional labelling algorithm to find an elementary path (one without repeating nodes). Such algorithm has been implemented by @pylgrim.

@righini2006 introduced a bidirectional labelling algorithm for the SPPRC. The bidirectional algorithm is an extension of the monodirectional algorithm that supports search from both ends of the graph, hence, reducing the computational efforts.
More recently, @Tilk2017 developed a bidirectional labelling algorithm with dynamic halfway point. The bidirectional search is bounded for both directions and these bounds are dynamically updated as the search in either direction advances. The algorithm has shown to be significantly more efficient that monodirectional ones [@gschwind2018].

Even with some of the most recent algorithms, solving an instance of the SPPRC can be slow, thus, heuristic algorithms have been developed.
Local search or metaheuristics start with a given path and perform a series of moves (edge/node deletion, insertion, or exchange) to obtain another feasible path with lower cost.
Some metaheuristics developed include, Tabu search [@desaulniers2008tabu], hybrid particle swarm algorithm [@marinakis2017hybrid], and, greedy randomised adaptive search procedure (GRASP) [@Ferone2019].

``cspy`` implements several of these recent exact and metaheuristic algorithms including:

- Bidirectional labeling algorithm with dynamic halfway point [@Tilk2017]; which includes the bidirectional labeling algorithm with static halfway point, and the monodirectional forward and backward labeling algorithms;
- Tabu search. Adapted from @desaulniers2008tabu;
- Greedy elimination procedure;
- Greedy Randomised Adaptive Search Procedure (GRASP). Adapted from @Ferone2019;
- Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology (PSOLGENT) @marinakis2017hybrid.

# Features

A key component of a CSP problem is to define a set of resources and a function to apply for these to evolve through the graph. Such functions are typically referred to as resource extension functions (REFs). The simplest REF is an additive one, where every time an edge is traversed a constant unit of a certain resource is consumed. However, custom and more generic REFs can be used.

``cspy`` allows for custom and generic REFs to be used. Hence, allowing for a custom consumption of the resources through the graph.

# Example

Consider the following problem. 

*Example.* Jane is part-time postwoman working in Delft, Netherlands. However, she is assigned a small area (the Indische Buurt neighbourhood) so when planning her daily route she wants to make it as long and exciting as possible. 
That is, when planning her routes she has to consider the total shift time, sights visited, travel time, and delivery time. Her shift has to be at most 5 hours.


This problem can easily be modelled as a CSP problem. 
With the description above, the set of resources can be defined as,

```python
R = ['sights', 'shift', 'travel-time', 'delivery-time'] 
# len(R) = 4
```

Let ``G`` denote a directed graph with edges to/from all streets of the Indische Buurt neighbourhood. Each edge has an attribute ``weight`` proportional to the distance (in km) between the two nodes and an attribute ``res_cost`` which is an array (specifically, a ``numpy.array``) with length ``len(R)``. To maximise the distance of the path, as required by Jane, we simple negate the distance, hence, solving a shortest path problem with negative distance will be the equivalent to solving a longest path problem. The entries of ``res_cost`` have the same order as the entries in ``R``.
The first entry of this array, corresponds to the ``'sights'`` resource, i.e. how many sights there are along a specific edge. The last entry of this array, corresponds to the ``'delivery-time'`` resource, i.e. time taken to deliver post along a specific edge. The remaining entries can be initialised to be 0.
Also, when defining ``G``, one has to specify the number of resources ``n_res``, which also has to be equal to ``len(R)``.

```python
from networkx import DiGraph

G = DiGraph(directed=True, n_res=4)  # init network
```

Now let's assume we have a function ``generate_district_network`` that can create the appropriate network.

```python
from read_input import generate_district_network  
# function to generate network from data

G = generate_district_network()
n_edges = len(G.edges())  # number of edges in network
```

To define the custom REFs,  ``jane_REF``, that controls how resources evolve throughout the path, we require two inputs: an array of current cumulative resource values ``res``, and the edge that is being considered for an extension of a path ``edge`` (which consists of two nodes and the edge data).

```python
from numpy import array

def jane_REF(res, edge):
    arr = array(res)  # local array
    i, j, edge_data = edge[:]  # unpack edge
    # i, j : string, edge_data : dict
    # Update 'sights' resource
    arr[0] += edge_data['res_cost'][0]
    # Update 'travel-time' resource (distance/speed)
    arr[2] += - edge_data['weight'] / float(WALKING_SPEED)
    # Update 'delivery-time' resource
    arr[3] += edge_data['res_cost'][3]
    # Update 'shift' resource
    arr[1] += (arr[2] + arr[3])  # travel-time + delivery-time
    return arr
```

Using ``cspy``, Jane can obtain a route ``path`` subject to her constraints as,

```Python
from cspy import Tabu, GRASP

SHIFT_DURATION = 5
# Maximum resources
max_res = [n_edges, SHIFT_DURATION, SHIFT_DURATION, SHIFT_DURATION]
# Minimum resources
min_res = [0, 0, 0, 0]
# Use Tabu Algorithm
path = Tabu(G, max_res, min_res, REF=jane_REF).run()
# Use GRASP algorithm
path = GRASP(G, max_res, min_res, REF=jane_REF).run()
```

Hence, each resource is restricted and updated as follows:


- ``'sights'`` : the cumulative number of sights visited has a dummy upper bound equal to the number of edges in the graph as there is no restriction to as how many sights Jane visits. Additionally, the value of this resource in the final path, will provide us with the accumulated number of sights in the path;
- ``'shift'`` : the cumulative shift time is updated as the travel time along the edge plus the delivery time, the upper bound of ``SHIFT_DURATION`` ensures that Jane doesn't exceed her part-time hours;
- ``'travel-time'`` : the cumulative travel time is updated using the positive distance travelled (``-edge_data['weight']``) over an average walking speed. Given the relationship between this resource and ``'shift'``, a maximum of the shift duration provides no restriction;
- ``'delivery-time'`` : the cumulative delivery time is simply updated using edge data. Similarly as for the previous resource, a maximum of the shift duration provides no restriction.

If we wish to implement the bidirectional labelling algorithm, we have to invert ``jane_REF``. In this case, it can be easily done,

```python
def jane_REF_backward(res, edge):
    arr = array(res)  # local array
    i, j, edge_data = edge[:]  # unpack edge
    # i, j : string, edge_data : dict
    # Update 'sights' resource
    arr[0] -= edge_data['res_cost'][0]
    # Update 'travel-time' resource (distance/speed)
    arr[2] -= - edge_data['weight'] / float(WALKING_SPEED)
    # Update 'delivery-time' resource
    arr[3] -= edge_data['res_cost'][3]
    # Update 'shift' resource
    arr[1] -= (arr[2] + arr[3])  # travel-time + delivery-time
    return arr
```

Now we can run the bidirectional labelling algorithm for an exact solution

```python
from cspy import BiDirectional

# Use BiDirectional algorithm
path = BiDirectional(G, max_res, min_res, REF_forward=jane_REF,
                     REF_backward=jane_REF_backward).run()
```

To see a real implementation of this example, please see @jpath.

# Acknowledgements

The author gratefully acknowledges the support of the EPSRC funded EP/L015692/1 STOR-i Centre for Doctoral Training. 

# References
