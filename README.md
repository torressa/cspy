[![CircleCI](https://circleci.com/gh/torressa/cspy/tree/master.svg?style=svg&circle-token=910e28b03dd0d32967fae038a3cf28b6cdf56334)](https://circleci.com/gh/torressa/cspy/tree/master)
[![codecov](https://codecov.io/gh/torressa/cspy/branch/master/graph/badge.svg?token=24tyrWinNT)](https://codecov.io/gh/torressa/cspy)

# cspy

A collection of algorithms for the (resource) Constrained Shortest Path problem.

The algorithms implemented include:

 [X] Monodirectional forward labeling algorithm;
 [X] Monodirectional backward labeling algorithm;
 [X] Bidirectional labeling algorithm with static halfway point;
 [X] Bidirectional labeling algorithm with dynamic halfway point [^fn1];
 [X] Heuristic Tabu search [^fn2].

Features implemented include: generic resource extension functions (not restricted to additive resources), generic resource consumptions (not restricted to non-negative values), and, increased efficiency (when compared to other implementations of monodirectional algorithms) [^fn3].


**TODO**
***

 [ ] Implement generic resource extension functions for bidirectional algorithm
 [ ] Tabu clean up
 
**Changelog**
***

pre-release v0.0.1: 20/06/2019

```
	Implemented Heuristic Tabu Search.
	Documentation updates.
		- docstring modifications to include maths


```

[^fn1]: https://www.sciencedirect.com/science/article/pii/S0377221717302035
[^fn2]: To appear.
[^fn3]: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints
