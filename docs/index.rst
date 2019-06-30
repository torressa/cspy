`cspy` Documentation
====================

`cspy` is an open source Python package that gathers some algorithms to solve the (resource) Constrained Shortest Path problem.


By setting different options when calling the algorithms, one can have up to five different algorithms.

 - Monodirectional forward labeling algorithm;
 - Monodirectional backward labeling algorithm;
 - Bidirectional labeling algorithm with static halfway point;
 - Bidirectional labeling algorithm with dynamic halfway point (`Tilk 2017`_);
 - Heuristic Tabu search.

.. Features implemented include: generic resource extension functions (`Inrich 2005`_) (not restricted to additive resources), generic resource consumptions (not restricted to non-negative values), and, increased efficiency (when compared to other implementations of monodirectional algorithms).

`cspy` is installable via `pip` (see `Getting Started`_) or the source code is made available here_.

.. _here: https://github.com/torressa/cspy
.. _Getting Started: https://cspy.readthedocs.io/en/latest/getting_started.html

.. toctree::
    :maxdepth: 2
    :caption: User Guide

    getting_started
    how_to





.. toctree::
   :maxdepth: 1
   :caption: API

   api/cspy.BiDirectional
   api/cspy.Tabu
   api/cspy.check_and_preprocess
   api/cspy.Label

    
    

.. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
