`cspy` Documentation
====================

`cspy` is an open source Python package that gathers some algorithms to solve
the (resource) Constrained Shortest Path (CSP) problem. The CSP problem has been studied in the
mathematical optimisation literature as allows the modelling of a wide range of problems.
They have proven useful in a wide variety of problems including:
the vehicle routing problem with time windows,
the technician routing and scheduling problem,
the capacitated arc-routing problem,
on-demand transportation systems, aircraft scheduling,
and, airport ground movement.

By setting different options when calling the algorithms,
one can have up to five different algorithms (exact and metaheuristic).

 - Monodirectional forward labeling algorithm (exact);
 - Monodirectional backward labeling algorithm (exact);
 - Bidirectional labeling algorithm with static halfway point (exact);
 - Bidirectional labeling algorithm with dynamic halfway point (exact) (`Tilk et al 2017`_);
 - Heuristic Tabu search (metaheuristic);
 - Greedy Elimination Procedure (metaheuristic);
 - Greedy Randomised Adaptive Search Procedure (GRASP) (metaheuristic). Adapted from `Ferone et al 2019`_.
 - Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology (PSOLGENT) (metaheuristic) (`Marinakis et al 2017`_).

Features implemented include:
generic resource extension functions (`Inrich 2005`_) (not restricted to additive resources),
generic resource consumptions (not restricted to non-negative values),
and, increased efficiency
(when compared to other implementations of monodirectional algorithms).

`cspy` is installable via `pip` (see `Getting Started`_) or the source code is made available here_.

.. _here: https://github.com/torressa/cspy
.. _Getting Started: https://cspy.readthedocs.io/en/latest/getting_started.html

.. toctree::
    :maxdepth: 2
    :caption: User Guide

    getting_started
    how_to
    ref

.. toctree::
   :maxdepth: 1
   :caption: Python API

   python_api/cspy.BiDirectional
   python_api/cspy.Tabu
   python_api/cspy.GreedyElim
   python_api/cspy.GRASP
   python_api/cspy.PSOLGENT
   python_api/cspy.preprocess_graph
   python_api/cspy.check

.. toctree::
   :maxdepth: 1
   :caption: C++ API

   cc_api/BiDirectional
   cc_api/Search
   cc_api/REFCallback
   cc_api/params
   cc_api/DiGraph
   cc_api/Vertex
   cc_api/Label
   cc_api/preprocessing



.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
.. _Tilk et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Marinakis et al 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302357z
.. _Ferone et al 2019: https://www.tandfonline.com/doi/full/10.1080/10556788.2018.1548015
