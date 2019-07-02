Using `cspy`
============

Here is the guide of how to use the `cspy` package.

Initialisations
~~~~~~~~~~~~~~~

In order to use `cspy` package and the algorithms within, first, one has to create a graph on which to apply the algorithms. 

To do so, we make use of the well-known `networkx` package. To be able to apply resource constraints, we have the following input graph requirements,


 - Graph must be a :class:`networkx.DiGraph`;
 - Graph must have an attribute `n_res` (set when initialising the graph) which determines the number of resources we are considering for the particular problem;
 - Graph must have a single `Source` and `Sink` nodes with no incoming or outgoing edges respectively;
 - Edges must have `res_cost` and `weight` attributes.

In order to run the algorithms create a appropriate algorithm instance (with the corresponding inputs) and call `run()`.

Please see individual algorithm documentation (BiDirectional_, Tabu_, GreedyElim_) for examples.

.. _BiDirectional: https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html
.. _Tabu: https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html
.. _GreedyElim: https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html

Prerequirements
~~~~~~~~~~~~~~~

For the :class:`BiDirectional` algorithm, there is a number of assumptions required (`Tilk et al 2017`_).

 1. The first resource must be a monotone resource;
 2. The resource extension are invertible.

For assumption 1, resource can be either artificial, such as the number of edges in the graph, or real like for example time. Clearly, these are problem-dependent and if your problem doesn't seem to have a monotone resource, it is easier to use an artificial one.
This allows for the monotone resource to comparable for the forward and backward directions. In practice, this means, using the first element in both edge attributes and input limits to be said monotone resource.

For assumption 2, if resource extension functions are additive, these are easily invertible.

.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
