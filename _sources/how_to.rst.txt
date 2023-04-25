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

If you are interested in custom resource extension functions, see the `REFs`_ section.

Examples
~~~~~~~~

The following examples are included in the `examples`_ for more in-depth usage.

- `vrpy`_: (under development) external vehicle routing framework which uses ``cspy`` to solve different variants of the vehicle routing problem using column generation.
- `jpath`_ : Simple example showing the necessary graph adptations and the use of custom resource extension functions. Also discussed below.
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
.. _REFs: https://cspy.readthedocs.io/en/latest/ref.html


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
        G = DiGraph(directed=True, n_res=4)  # init network with 4 resources

Now, using the open source package OSMnx, we can easily generate a network for Jane's neighbourhood

.. code-block:: python

        from osmnx import graph_from_address, plot_graph

        M = graph_from_address('Ceramstraat, Delft, Netherlands',
                                   distance=1600,
                                   network_type='walk',
                                   simplify=False)


We have to transform the network for one compatible with ``cspy``,
as per the `Input Requirements`_.
The following code will convert a city map into a directed graph,
rename the start/end nodes of Janes walk to be ``Source`` and ``Sink`` (names which ``cspy`` uses),
and calculate the specifics of Jane's walk (figuring out travel time, adding buildings/sights, etc).

.. code-block:: python

        from networkx import DiGraph
        from jpath_preprocessing import relabel_source_sink, add_cspy_edge_attributes

        # Transform M from networkx.MultiGraph to networkx.DiGraph
        # This is requirement by the algorithms
        G = DiGraph(M, directed=True, n_res=4)

        # Relabel nodes the start/end nodes as "Source"/"Sink"
        # (The post-office is in Ternatestraat and Jane's home is in Delftweg)
        G = relabel_source_sink(G, {"Source": "Ternatestraat", "Sink": "Delftweg"})

        # Add Jane's specific resources to the edges
        # (For each edge, adds a `res_cost` attribute with an array with the resources consumed along the specific edge)
        G = add_cspy_edge_attributes(G)


To define the custom REFs,  ``jane_REF``, that controls how resources evolve throughout the path,
we require two inputs: an array of current cumulative resource values ``res``,
and the edge that is being considered for an extension of a path ``edge``
(which consists of two nodes and the edge data).


.. code-block:: python

        from numpy import array
        from cspy import REFCallback

        WALKING_SPEED = 3

        class MyCallback(REFCallback):

            def __init__(self):
                REFCallback.__init__(self)
                # Empty attribute for later
                self.G = None

            def REF_fwd(self, cumul_res, tail, head, edge_res, partial_path,
                        cumul_cost):
                new_res = list(cumul_res)
                i, j = tail, head
                # Monotone resource
                new_res[0] += 1
                # Update 'sights' resource
                new_res[1] += self.G.edges[i,j]['res_cost'][1]
                # Extract the 'travel-time' resource (distance/speed)
                new_res[3] = - self.G.edges[i,j]['weight'] / float(WALKING_SPEED)
                # # Update 'delivery-time' resource
                new_res[4] = self.G.edges[i,j]['res_cost'][4]
                # # Update 'shift' resource
              new_res[2] += (new_res[3] + new_res[4])  # travel-time + delivery-time
              return new_res


Hence, each resource is restricted and updated as follows:


- ``'sights'`` : the cumulative number of sights visited has a dummy upper bound equal to the number of edges in the graph as there is no restriction to as how many sights Jane visits. Additionally, the value of this resource in the final path, will provide us with the accumulated number of sights in the path;
- ``'shift'`` : the cumulative shift time is updated as the travel time along the edge plus the delivery time, the upper bound of ``SHIFT_DURATION`` ensures that Jane doesn't exceed her part-time hours;
- ``'travel-time'`` : the cumulative travel time is updated using the positive distance travelled (``-edge_data['weight']``) over an average walking speed. Given the relationship between this resource and
- ``'shift'`` : a maximum of the shift duration provides no restriction.
- ``'delivery-time'`` : the cumulative delivery time is simply updated using edge data. Similarly as for the previous resource, a maximum of the shift duration provides no restriction.


Using ``cspy``, Jane can obtain a route ``path`` and subject to her constraints as,

.. code-block:: python

        from cspy import Tabu, BiDirectional

        n_edges = len(G.edges())  # number of edges in network
        max_res = [n_edges, 5*n_edges, 5, 5, 5]
        min_res = [0, 0, 0, 0, 0]

        my_callback = MyCallback()
        alg = BiDirectional(G,
                            max_res,
                            min_res,
                            REF_callback=my_callback,
                            direction="forward",
                            elementary=True)
        # Pass preprocessed graph
        my_callback.G = alg1.G
        alg.run()
        print(alg.path)  # print route


Additionally, we can query other useful attributes as

.. code-block:: python

        alg.total_cost
        alg.consumed_resources



.. _jpath: https://github.com/torressa/cspy/tree/master/examples/jpath
.. _cgar: https://github.com/torressa/cspy/blob/master/examples/cgar/cgar.pdf
.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
.. _unittest: https://github.com/torressa/cspy/tree/master/test/python/tests_issue32.py
.. _Input Requirements: https://cspy.readthedocs.io/en/latest/how_to.html#input-requirements
