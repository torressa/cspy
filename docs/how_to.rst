Using `cspy`
============

Here is the guide of how to use the `cspy` package.

Initialisations
~~~~~~~~~~~~~~~

In order to use `cspy` package and the algorithms within, first, one has to create a directed graph on which to apply the algorithms. 

To do so, we make use of the well-known `networkx` package. To be able to apply resource constraints, we have the following input graph requirements,


 - Graph must be a :class:`networkx.DiGraph`;
 - Graph must have an attribute ``n_res`` (set when initialising the graph) which determines the number of resources we are considering for the particular problem;
 - Graph must have a single `Source` and `Sink` nodes with no incoming or outgoing edges respectively;
 - Edges must have ``res_cost`` (of type :class:`numpy.array`) and ``weight`` attributes.

For example,

.. code-block:: python

        >>> from networkx import DiGraph
        >>> from numpy import array
        >>> G = DiGraph(directed=True, n_res=2)
        >>> G.add_edge('Source', 'A', res_cost=array([1, 0]), weight=1.0)
        >>> G.add_edge('A', 'B', res_cost=array([1, 0]), weight=1.0)
        >>> G.add_edge('B', 'Sink', res_cost=array([1, 0]), weight=1.0)

Algorithms
~~~~~~~~~~

Have a look and choose which algorithm you'd like to use. In order to run the algorithms create a appropriate algorithm instance (with the appropriate inputs) and call ``run()``.

- :class:`BiDirectional`: `Bidirectional and monodirectional algorithms`_
- :class:`Tabu` `Heuristic Tabu Search`_
- :class:`GreedyElim` `Greedy Elimination Procedure`_
- :class:`GRASP` `GRASP`_
- :class:`PSOLGENT` `Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology`_ (PSOLGENT)

The first algorithm :class:`BiDirectional`, is the only *exact* algorithm in the library. This means that it provides an exact (optimal) solution to the resource CSP problem. For this reason, it sometimes takes longer than the others. The remaining algorithms are metaheuristics, i.e. they provide fast and approximate solutions to the CSP problem.

Please see individual algorithm documentation for simple examples.

Please see `jpath`_ for a more in-depth example.

.. _Bidirectional and monodirectional algorithms: https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html
.. _Heuristic Tabu Search: https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html
.. _Greedy Elimination Procedure: https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html
.. _Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology: https://cspy.readthedocs.io/en/latest/api/cspy.PSOLGENT.html
.. _GRASP: https://cspy.readthedocs.io/en/latest/api/cspy.GRASP.html
.. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302357z
.. _jpath: https://github.com/torressa/jpath

Pre-requirements
~~~~~~~~~~~~~~~~

For the :class:`BiDirectional` algorithm, there is a number of assumptions required (`Tilk et al 2017`_).

 1. The first resource must be a monotone resource;
 2. The resource extension functions are invertible.

For assumption 1, the resource can be either artificial, such as the number of edges in the graph, or real, for example time.
This allows for the monotone resource to comparable for the forward and backward directions. In practice, this means, that ``n_res = len(max_res) = len(min_res)``:math:`\geq 2`, and that the first element in both edge attributes and input limits is the monotone resource.

For assumption 2, if resource extension functions are additive, these are easily invertible. However, custom resource extension functions, it is up to the user to define them appropriately.

REFs
~~~~

Additive resource extension functions (REFs), are implemented by default in all the algorithms. However, you can use your own custom REFs. This allows the modelling of more complex relationships and more realistic evolution of resources.

For theoretical information on what REFs are we refer you to the paper by `Inrich 2005`_. For a practical implementation see `jpath`_.

Practically, if the users wished for more control on the propagation of resources, a custom REF can be defined as follows. First, the function will need two inputs: ``res``, a cumulative resource array, and ``edge``, an edge to consider for the extension of the current partial path. This function will be called every time the algorithms wish to consider and edge as part of the shortest path.

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


.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
