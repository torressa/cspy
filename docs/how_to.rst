Using ``cspy``
==============

Here is the guide of how to use the ``cspy`` package.

Initialisations
~~~~~~~~~~~~~~~
In order to use ``cspy`` package and the algorithms within, first, one has to create a graph on which to apply the algorithms. To do so, we make use of the well-known ``networkx`` package. In order to be apply resource constraint, we define a graph attribute ``n_res`` which determines the number of resources we are considering for the particular problem. In order to define the resource consumption and to find the shortest path, the edges have a ``res_cost`` and a ``weight`` attribute. Furthermore, the graph must have a single ``Source`` and ``Sink`` nodes with no incoming or outgoing edges respectively.

In order to run the algorithm, we use the :class:`cspy.Bidirectional` class. To initiliase it, the only non-optional inputs are, ``G`` the digraph of interest (object ``networkx.DiGraph``), and, ``max_res`` and ``min_res``, both lists of floats of equal length (>= 2). 

The reason for this is due to the nature of the algorithm and the prerequirement that one of the resources must be a monotone resource. Such a resource can be either artificial, such as the number of edges in the graph, or real like for example time. Clearly, these are problem-dependent and if your problem doesn't seem to have a monotone resource, it is easier to use an artificial one.
This allows for the monotone resource to comparable for the forward and backward directions. In practice, this means, using the first element in both edge attributes and input limits to be said monotone resource (`Tilk 2017`_).

.. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
