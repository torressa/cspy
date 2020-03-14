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

Please see the `examples`_ for more in-depth usage.

Please see individual algorithm documentation for simple examples.

.. _Bidirectional and monodirectional algorithms: https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html
.. _Heuristic Tabu Search: https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html
.. _Greedy Elimination Procedure: https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html
.. _Particle Swarm Optimization with combined Local and Global Expanding Neighbourhood Topology: https://cspy.readthedocs.io/en/latest/api/cspy.PSOLGENT.html
.. _GRASP: https://cspy.readthedocs.io/en/latest/api/cspy.GRASP.html
.. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302357z
.. _examples: https://github.com/torressa/cspy/examples/

Pre-requirements
~~~~~~~~~~~~~~~~

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

REFs
~~~~

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
For a brief overview with a practical implementation see the `examples`_ and 
the pdf document `cgar`_.

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

.. _cgar: https://github.com/torressa/cspy/examples/cgar/cgar.pdf
.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints

