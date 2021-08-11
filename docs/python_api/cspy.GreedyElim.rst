cspy.GreedyElim
===============

.. automodule:: cspy.GreedyElim
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
To run the algorithm, create a :class:`GreedyElim` instance and call `run`.

.. code-block:: python

    >>> from cspy import GreedyElim
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
    >>> greedelim = GreedyElim(G, max_res, min_res)
    >>> greedelim.run()
    >>> print(greedelim.path)
    ['Source', 'A', 'C', 'D', 'E', 'Sink']

