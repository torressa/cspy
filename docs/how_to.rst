Using `cspy`
============

Here is the guide of how to use the `cspy` package and the algorithms within.

Input Requirements
~~~~~~~~~~~~~~~~~~

In order to use `cspy` package and the algorithms within, first, one has to create a directed graph on which to apply the algorithms.

To do so, we make use of the well-known `networkx` package. 
To be able to apply resource constraints, we have the following input requirements,

 - Input graphs must be of type :class:`networkx.DiGraph`;
 - Input graphs must have an attribute ``n_res`` (set when initialising the graph) which determines the number of resources we are considering for the particular problem;
 - Input graphs must have a single `Source` and `Sink` nodes with no incoming or outgoing edges respectively;
 - Edges in the input graph must have ``res_cost`` (of type :class:`numpy.array`) and ``weight`` attributes.


For example the following simple network fulfills all the requirements listed above:

.. code-block:: python

        >>> from networkx import DiGraph
        >>> from numpy import array
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=array([1, 0]), weight=1.0)
        >>> G.add_edge('A', 'B', res_cost=array([1, 0]), weight=1.0)
        >>> G.add_edge('B', 'Sink', res_cost=array([1, 0]), weight=1.0)

The algorithms have some common inputs and requirements,

 - Two lists ``max_res`` and ``min_res``, with lists of the maximum and minimum resource usage to be enforced for the resulting path; 
 - Input graphs must not contain any negative cost cycles.

For former, the user must ensure consistency between the index in ``res_cost`` and
the index in ``max_res``\``min_res``, such that it corresponds to the same resource.
The latter, is due to the fact that some algorithms depend standard shortest path algorithms
(specifically :class:`networkx.astar_path`), hence, they get stuck.

Algorithms
~~~~~~~~~~

Have a look and choose which algorithm you'd like to use. 
In order to run the algorithms create a appropriate algorithm instance, say ``alg``,
(with the appropriate inputs), call ``alg.run()``, and then access the different elements from the solution.
Attributes include ``alg.path`` for a list with the nodes in the path, 
``alg.total_cost`` for the accumulated cost of the path,
and ``alg.consumed_resources`` for the accumulated resource usage of the path.
 
- :class:`BiDirectional`: `Bidirectional and monodirectional algorithms`_
- :class:`Tabu` `Heuristic Tabu Search`_
- :class:`GreedyElim` `Greedy Elimination Procedure`_
- :class:`GRASP` `GRASP`_
- :class:`PSOLGENT` `Particle Swarm Optimization with combined Local and Global Expanding Neighbourhood Topology`_ (PSOLGENT)

The first algorithm :class:`BiDirectional`, is the only *exact* algorithm in the library.
This means that it provides an exact (optimal) solution to the resource CSP problem.
For this reason, it sometimes takes longer than the others.
The remaining algorithms are metaheuristics,
i.e. they provide fast and approximate solutions to the CSP problem.

Examples
~~~~~~~~

The following examples are included in the `examples`_ for more in-depth usage.

- `jpath`_ : Simple example showing the necessary graph adptations and the use of custom resource extension functions. Also discussed below.
- `vrpy`_: (under development) external vehicle routing framework which uses ``cspy`` to solve different variants of the vehicle routing problem using column generation.
- `cgar`_: Complex example using ``cspy`` for column generation applied to the aircraft recovery problem.

Please see individual algorithm documentation for simple examples.

.. _Bidirectional and monodirectional algorithms: https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html
.. _Heuristic Tabu Search: https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html
.. _Greedy Elimination Procedure: https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html
.. _Particle Swarm Optimization with combined Local and Global Expanding Neighbourhood Topology: https://cspy.readthedocs.io/en/latest/api/cspy.PSOLGENT.html
.. _GRASP: https://cspy.readthedocs.io/en/latest/api/cspy.GRASP.html
.. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302357z
.. _examples: https://github.com/torressa/cspy/tree/master/examples/
.. _vrpy: https://github.com/Kuifje02/vrpy

REFs
~~~~

Pre-requirements
****************

For the :class:`BiDirectional` algorithm, there is a number of assumptions required by definition (`Tilk et al 2017`_).

 1. The first resource must be a monotone resource;
 2. The resource extension functions are invertible.

For assumption 1, the resource can be either artificial,
such as the number of edges in the graph, or real, for example time.
This allows for the monotone resource to be comparable for the forward and backward directions.
In practice, this means, that ``res_cost[0]``, ``max_res[0]``,
and ``min_res[0]`` correspond to the monotone resource;
and that we must have at least two resources
(the monotone one and the one you wish to model; otherwise you might as well use a standard
shortest path algorithm!) (i.e. ``n_res = len(max_res) = len(min_res)``:math:`\geq 2`),
and that the first element in both edge attributes and input limits refer to the monotone
resource.

The bounds chosen for the monotone resource
(``max_res[0]`` and ``min_res[0]``), effectively represent the halfway points for the
algorithm. Hence unless ``max_res[0]``:math`>```min_res[0]``, the searches will not reach
either end of the graph and the resulting path will be erroneous.
Additionally, occasionally, the resource limits do not allow for a feasible path to be found.
Some preprocessing routines have been implemented for the case of additive REFs.

For assumption 2, if resource extension functions are additive, these are easily invertible (i.e. add in the forward direction and subtract in the backward direction).
However, when using custom resource extension functions (discussed below),
it is up to the user to define them appropriately!

Additive REFs
*************

Additive resource extension functions (REFs), are implemented by default in all the algorithms.
If left unchanged, this means that resources propagate in the following fashion. 
Suppose we are considering extending partial path :math:`p_i` 
(a path from the source to node :math:`i`), along edge :math:`(i, j)`.
Under the assumption that edge :math:`(i, j)` has a resource cost defined 
(one for each of the resources); 
the partial path :math:`p_j` (a path from the source to node :math:`j` passing 
through node :math:`i`) will have a resource consumption equal to the total resource accumulated along :math:`p_i` plus the resource cost of edge :math:`(i, j)`.
If for instance, this resource consumption for a given resource exceeds the limit given in 
As discussed above, the resource costs are defined by the user in the input graph.

Custom REFs
***********

Additionally, users can implement their own custom REFs. 
This allows the modelling of more complex relationships and more realistic evolution 
of resources.
However, it is up the users to ensure that the custom REFs are well defined,
it may be the case that the algorithm fails to find a feasible path, or gets stuck.

For theoretical information on what REFs are we refer you to the paper by `Inrich 2005`_.
For a brief overview with a practical implementation see any of the `examples`_.

Custom REF template
*******************

Practically, if the users wished for more control on the propagation of resources,
a custom REF can be defined as follows.
First, the function will need two inputs: ``res``, a cumulative resource array, and ``edge``, an edge to consider for the extension of the current partial path. This function will be called every time the algorithms wish to consider and edge as part of the shortest path.

As an example, suppose the 2nd resource represents travel time (``res[1]``). Suppose the edge weight contains the travel time. Hence, every time an edge is traversed, the ``res[1]`` is updated by adding its previous cumulative value and the current edge weight. We can define our custom REF as follows,

.. code-block:: python

        from numpy import array

        def REF_custom(cumulative_res, edge):
        	new_res = array(cumulative_res)
        	# your filtering criteria that changes the elements of new_res
        	# For example:
        	head_node, tail_node, egde_data = edge[0:3]
        	new_res[1] += edge_data['weight']
        	return new_res

Your custom REF can then be passed with this format, into the algorithm of choice using the ``REF`` argument (see individual algorithms for details). Note that for the :class:`BiDirectional` algorithm, due to the properties of the algorithm, if you want to use this feature, you have to pass two custom REFs: one for the forward search and one for the backward search. Where the backward REF has to be the inverse of the forward REF, otherwise the algorithm will not return a meaningful path (`Tilk et al 2017`_). It is up to the user to ensure this is the case.


Simple Example
~~~~~~~~~~~~~~

For illustration of most of the things discussed above, consider the following example.

Jane is part-time postwoman working in Delft, Netherlands. However, she is assigned a small area (the Indische Buurt neighbourhood) so when planning her daily route she wants to make it as long and exciting as possible. 
That is, when planning her routes she has to consider the total shift time, sights visited, travel time, and delivery time. Her shift has to be at most 5 hours.


This problem can easily be modelled as a CSP problem. 
With the description above, the set of resources can be defined as,

.. code-block:: python
    R = ['sights', 'shift', 'travel-time', 'delivery-time'] 
    # len(R) = 4

Let ``G`` denote a directed graph with edges to/from all streets of the Indische Buurt 
neighbourhood. 
Each edge has an attribute ``weight`` and an attribute ``res_cost`` which is an array (specifically, a ``numpy.array``)
with length ``len(R)``. 
The entries of ``res_cost`` have the same order as the entries in ``R``.
The first entry of this array, corresponds to the ``'sights'`` resource, i.e. how many sights there are along a specific edge. The last entry of this array, corresponds to the ``'delivery-time'`` resource, i.e. time taken to deliver post along a specific edge. The remaining entries can be initialised to be 0.
Also, when defining ``G``, one has to specify the number of resources ``n_res``, which also has to be equal to ``len(R)``.

.. code-block:: python
    from networkx import DiGraph
    G = DiGraph(directed=True, n_res=4)  # init network

Now, using the open source package OSMnx, we can easily generate a network for Jane's neighbourhood

.. code-block:: python
    from osmnx import graph_from_address, plot_graph

    M = graph_from_address('Ceramstraat, Delft, Netherlands',
                               distance=1600,
                               network_type='walk',
                               simplify=False)

We have to transform the network for one compatible with cspy.
To do this suppose we have two functions from ``jpath_preprocessing`` 
that perform all the changes required 
(for more details, see `jpath`_)

.. code-block:: python
    from networkx import DiGraph
    from jpath_preprocessing import relabel_source_sink, add_cspy_edge_attributes

    # Transform M to comply with cspy's prerequirements
    # Convert MultiGraph into a Digraph with attribute 'n_res'
    G = DiGraph(M, directed=True, n_res=5)
    # Relabel source node to "Source" and sink node to "Sink" (see function for more details)
    G = relabel_source_sink(G)
    # Add res_cost and other resource attributes (see function for more details)
    G = add_cspy_edge_attributes(G)

    n_edges = len(G.edges())  # number of edges in network

To define the custom REFs,  ``jane_REF``, that controls how resources evolve throughout the path,
we require two inputs: an array of current cumulative resource values ``res``, 
and the edge that is being considered for an extension of a path ``edge``
(which consists of two nodes and the edge data).

.. code-block:: python
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


Hence, each resource is restricted and updated as follows:


- ``'sights'`` : the cumulative number of sights visited has a dummy upper bound equal to the number of edges in the graph as there is no restriction to as how many sights Jane visits. Additionally, the value of this resource in the final path, will provide us with the accumulated number of sights in the path;
- ``'shift'`` : the cumulative shift time is updated as the travel time along the edge plus the delivery time, the upper bound of ``SHIFT_DURATION`` ensures that Jane doesn't exceed her part-time hours;
- ``'travel-time'`` : the cumulative travel time is updated using the positive distance travelled (``-edge_data['weight']``) over an average walking speed. Given the relationship between this resource and 
- ``'shift'`` : a maximum of the shift duration provides no restriction.
- ``'delivery-time'`` : the cumulative delivery time is simply updated using edge data. Similarly as for the previous resource, a maximum of the shift duration provides no restriction.


Using ``cspy``, Jane can obtain a route ``path`` and subject to her constraints as,

.. code-block:: python
    from cspy import Tabu
    SHIFT_DURATION = 5
    # Maximum resources
    max_res = [n_edges, SHIFT_DURATION, SHIFT_DURATION, SHIFT_DURATION]
    # Minimum resources
    min_res = [0, 0, 0, 0]
    # Use Tabu Algorithm
    tabu = Tabu(G, max_res, min_res, REF=jane_REF).run()
    print(tabu.path)  # print route


Additionally, we can query other useful attributes as

.. code-block:: python
    tabu.total_cost
    tabu.consumed_resources


.. _jpath: https://github.com/torressa/cspy/tree/master/examples/jpath
.. _cgar: https://github.com/torressa/cspy/blob/master/examples/cgar/cgar.pdf
.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints

