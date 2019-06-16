Using `cspy`
============

Here is the guide of how to use the `cspy` package.

Initialisations
~~~~~~~~~~~~~~~
In order to use `cspy` package and the algorithms within, first, one has to create a graph on which to apply the algorithms. To do so, we make use of the well-known `networkx` package. In order to be apply resource constraint, we define a graph attribute `n_res` which determines the number of resources we are considering for the particular problem. In order to define the resource consumption and to find the shortest path, the edges have a `res_cost` and a `weight` attribute. Furthermore, the graph must have a single `Source` and `Sink` nodes with no incoming or outgoing edges respectively.

In order to run the algorithm, we use the :class:`~cspy.Bidirectional` class. To initiliase it, the only non-optional inputs are, `G` the digraph of interest (object `networkx.DiGraph`), and, `max_res` and `min_res`, both lists of floats of equal length (>= 2). 

The reason for this is due to the nature of the algorithm and the prerequirement that one of the resources must be a monotone resource. Such a resource can be either artificial, such as the number of edges in the graph, or real like for example time. Clearly, these are problem-dependent and if your problem doesn't seem to have a monotone resource, it is easier to use an artificial one.
This allows for the monotone resource to comparable for the forward and backward directions. In practice, this means, using the first element in both edge attributes and input limits to be said monotone resource (`Tilk 2017`_).

.. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035

Example Code
~~~~~~~~~~~~

Creating a simple graph with the first resource representing the number of edges.

.. code-block:: python

    >>> import cspy
    >>> import networkx as nx
    >>> G = nx.DiGraph(directed=True, n_res=2)
    >>> G.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
    >>> G.add_edge('A', 'B', res_cost=[1, 0.3], weight=0)
    >>> G.add_edge('A', 'C', res_cost=[1, 0.1], weight=0)
    >>> G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
    >>> G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
    >>> G.add_edge('C', 'Sink', res_cost=[1, 10], weight=0)
    >>> algObj = BiDirectional(G, max_res=[4, 20], min_res=[1, 0], direction='both')
    >>> path = algObj.run()
    >>> print(path)
    ['Source', 'A', 'B', 'C', 'Sink']

Hence, by the input limits, the maximum for the first and second resources are 4 and 20 respectively. The minimum for the first and second resources are 1 and 0 respectively. Due to the nature of the algorithm, the forward search is limited to first resource being <= 4 (so can only reach node C), while the backward search first resource > 1 (so can reach the source).

Resource Extension Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default... 