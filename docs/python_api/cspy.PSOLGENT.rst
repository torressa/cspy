cspy.PSOLGENT
=============

.. automodule:: cspy.PSOLGENT
	:members:
   	:inherited-members:

 
Notes
-----
The input graph must have a ``n_res`` attribute.
The edges in the graph must all have a ``res_cost`` attribute.
Also, we must have ``len(min_res)`` :math:`=` ``len(max_res)``.
See `Using cspy`_.

This algorithm requires a consistent sorting of the nodes in the graph.
Please see comments and edit the function ``_sort_nodes`` accordingly.

.. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

Example
-------
.. code-block:: python

    >>> from cspy import PSOLGENT
    >>> from networkx import DiGraph
    >>> from numpy import zeros, ones, array
    >>> G = DiGraph(directed=True, n_res=2)
    >>> G.add_edge('Source', 'A', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('Source', 'B', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('Source', 'C', res_cost=array([10, 1]), weight=10)
    >>> G.add_edge('A', 'C', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('A', 'E', res_cost=array([10, 1]), weight=10)
    >>> G.add_edge('A', 'F', res_cost=array([10, 1]), weight=10)
    >>> G.add_edge('B', 'C', res_cost=array([2, 1]), weight=-1)
    >>> G.add_edge('B', 'F', res_cost=array([10, 1]), weight=10)
    >>> G.add_edge('B', 'E', res_cost=array([10, 1]), weight=10)
    >>> G.add_edge('C', 'D', res_cost=array([1, 1]), weight=-1)
    >>> G.add_edge('D', 'E', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('D', 'F', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('D', 'Sink', res_cost=array([10, 10]), weight=10)
    >>> G.add_edge('F', 'Sink', res_cost=array([10, 1]), weight=1)
    >>> G.add_edge('E', 'Sink', res_cost=array([1, 1]), weight=1)
    >>> n_nodes = len(G.nodes())
    >>> psolgent = PSOLGENT(G, [5, 5], [0, 0],
                            max_iter=200,
                            swarm_size=50,
                            member_size=n_nodes,
                            neighbourhood_size=50)
    >>> psolgent.run()
    >>> print(psolgent.path)
    ['Source', 'A', 'C', 'D', 'E', 'Sink']

