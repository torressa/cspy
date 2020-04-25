cspy.Tabu
=========

.. automodule:: cspy.Tabu
    :members:
   	:inherited-members:
 
Notes
-----
The input graph must have a ``n_res`` attribute.
The edges in the graph must all have a ``res_cost`` attribute.
See `Using cspy`_

.. _Using cspy: https://cspy.readthedocs.io/en/latest/how_to.html

Example
-------
To run the algorithm, create a :class:`Tabu` instance, call `run`, and then
query the attributes of interest: `path`, `total_cost`, or
`consumed_resources`.

.. code-block:: python

    >>> from cspy import Tabu
    >>> from networkx import DiGraph
    >>> from numpy import array
    >>> G = DiGraph(directed=True, n_res=2)
    >>> G.add_edge('Source', 'A', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('Source', 'B', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('A', 'C', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('B', 'C', res_cost=array([2, 1]), weight=-1)
    >>> G.add_edge('C', 'D', res_cost=array([1, 1]), weight=-1)
    >>> G.add_edge('D', 'E', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('D', 'F', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('F', 'Sink', res_cost=array([1, 1]), weight=1)
    >>> G.add_edge('E', 'Sink', res_cost=array([1, 1]), weight=1)
    >>> max_res, min_res = [5, 5], [0, 0]
    >>> tabu = Tabu(G, max_res, min_res)
    >>> tabu.run()
    >>> print(tabu.path)
    ['Source', 'A', 'C', 'D', 'E', 'Sink']

