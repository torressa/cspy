`cspy` Documentation
------------------
`cspy` is an open source Python package that gathers some well-known algorihtms to solve the resource constrained shortest path problem.

The algorithms implemented include: Bidirectional Labelling Algorithm (with dynamic and static halway points) (`Tilk 2017`_). This algorithm is a generalisation of the monodirectional labelling algorithm, which is included within. 

By setting different options when calling the algorithm, one can have up to four different algorithms.

 - Monodirectional forward labeling algorithm;
 - Monodirectional backward labeling algorithm;
 - Bidirectional labeling algorithm with static halfway point;
 - Bidirectional labeling algorithm with dynamic halfway point.

Features implemented include: generic resource extension functions (`Inrich 2005`_) (not restricted to additive resources), generic resource consumptions (not restricted to non-negative values), and, increased efficiency (when compared to other implementations of monodirectional algorithms).

`cspy` is installable via `pip` (see `Getting Started`_) or the source code is made avaliable here_.

.. _here: https://github.com/torressa/cspy
.. _PyPI: https://pypi.org/project/cspy
.. _Getting Started: https://cspy.readthedocs.io/en/latest/getting_started.html

.. toctree::
    :maxdepth: 2
    :caption: User Guide

    getting_started
    how_to


Documentation
------------

.. automodule:: cspy.algorithms
.. autosummary::
   :toctree: api/

   	cspy.BiDirectional
   	cspy.Tabu
   	cspy.check_and_preprocess
    cspy.Label

    
    

.. _Tilk 2017: https://www.sciencedirect.com/science/article/pii/S0377221717302035
.. _Inrich 2005: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
