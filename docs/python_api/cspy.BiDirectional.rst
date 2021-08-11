cspy.BiDirectional
==================

.. automodule:: cspy.BiDirectional
	:members:
   	:inherited-members:

Notes
-----
The input graph must have a ``n_res`` attribute equal to the number of resources.
The edges in the graph must all have a ``res_cost`` attribute (with size equal to  ``n_res``).

According to the inputs, four different algorithms can be used.

- ``direction`` = "forward": Monodirectional forward labeling algorithm
- :math:`H_F == H_B`: Bidirectional labeling algorithm with static halfway point.
- ``direction`` = "backward": Monodirectional backward labeling algorithm
- :math:`H_F > H_B`: Bidirectional labeling algorithm with dynamic halfway point.
- :math:`H_F < H_B`: The algorithm won't go anywhere!

Where :math:`H_F / H_B` are the first elements in the maximum / minimum resources arrays.

Example
-------
To run the algorithm, create a :class:`BiDirectional` instance and call
``run``.

.. code-block:: python

    >>> from cspy import BiDirectional
    >>> from networkx import DiGraph
    >>> from numpy import array
    >>> G = DiGraph(directed=True, n_res=2)
    >>> G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
    >>> G.add_edge("A", "B", res_cost=array([1, 0.3]), weight=0)
    >>> G.add_edge("A", "C", res_cost=array([1, 0.1]), weight=0)
    >>> G.add_edge("B", "C", res_cost=array([1, 3]), weight=-10)
    >>> G.add_edge("B", "Sink", res_cost=array([1, 2]), weight=10)
    >>> G.add_edge("C", "Sink", res_cost=array([1, 10]), weight=0)
    >>> max_res, min_res = [4, 20], [1, 0]
    >>> bidirec = BiDirectional(G, max_res, min_res, direction="both")
    >>> bidirec.run()
    >>> print(bidirec.path)
    ["Source", "A", "B", "C", "Sink"]
