---
title: 'cspy: A Python package with a collection of algorithms for the (Resource) Constrained Shortest Path problem'
tags:
  - Python
  - Resource Constrained Shortest path
  - Networks
  - Graph Theory
authors:
  - name: David Torres Sanchez
    orcid: 0000-0002-2894-9432
    affiliation: 1
affiliations:
 - name: STOR-i, Lancaster University, UK.
   index: 1
date: July 2019
bibliography: paper.bib
---

# Introduction

When solving the shortest path problem and considering multiple operational restrictions, one may resort to the (resource) constrained shortest path (CSP) problem. 
In the applied column generation framework, particularly in the scheduling related literature, the CSP problem is commonly employed to generate columns. It consists, as its name suggests, in finding, among all paths, the shortest path from source to sink nodes that satisfies a set of constraints for a defined set of resources. 

``cspy`` is a Python package that allows you to solve instances of the CSP problem using up to eight different algorithms.

The CSP problem was first introduced as a subproblem for the bus driver scheduling problem.
These have been shown to be applicable to a wide variety of problems including: the vehicle routing problem with time windows, the technician routing and scheduling problem, the capacitated arc-routing problem, on-demand transportation systems, and, airport ground movement [@Desrochers1988; @Feillet2004 @Inrich2006; @Righini2008; @Bode2014; @Chen2016; @GARAIX201062; @Tilk2017; @Zamorano2017]. 

# Algorithms

Even though the RCSPP is $\mathcal{NP}$-hard [@gary1979], several algorithms have been developed to solve it. The most common algorithms are dynamic programming labelling algorithms. 
@inrich presented an exact algorithm based on DP, the monodirectional forward labelling algorithm, based on the pioneering work by @Desrochers1988. 

Advanced and efficient algorithms have been developed since. @Boland2006 published a state augmenting algorithm that uses a monodirectional labelling algorithm to find an elementary path (one without repeating nodes). Such algorithm has been implemented by @pylgrim.

@righini2006 introduced a bidirectional labelling algorithm for the SPPRC. The bidirectional algorithm is an extension of the monodirectional algorithm that supports search from both ends of the graph, hence, reducing the computational efforts.
More recently, @Tilk2017 developed a bidirectional labelling algorithm with dynamic halfway point. The bidirectional search is bounded for both directions and these bounds are dynamically updated as the search in either direction advances. The algorithm has shown to be significantly more efficient that monodirectional ones [@gschwind2018].

Even with some of the most recent algorithms, solving an instance of the SPPRC can be slow, thus, heuristic algorithms have been developed.
Local search or metaheuristics start with a given path and perform a series of moves (edge/node deletion, insertion, or exchange) to obtain another feasible path with lower cost.
Some metaheuristics developed include, Tabu search [@desaulniers2008tabu], hybrid particle swarm algorithm [@marinakis2017hybrid], and, greedy randomised adaptive search procedure (GRASP) [@Ferone2019].

``cspy`` implements several of these recent exact and metaheuristic algorithms including:

- Bidirectional labeling algorithm with dynamic halfway point [@Tilk2017]; which includes the bidirectional labeling algorithm with static halfway point, and the monodirectional forward and backward labeling algorithms;
- Tabu search. Adapted from @desaulniers2008tabu;
- Greedy elimination procedure;
- Greedy Randomised Adaptive Search Procedure (GRASP). Adapted from @Ferone2019;
- Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology (PSOLGENT) [@marinakis2017hybrid].

The implementations allow for custom resource extension functions (REFs) to be used. Hence, allowing for generic consumption of the resources through the graph, not restricted to additive and subtractive REFs [@irnich2008]. 

``cspy`` is of interest to the operational research community and others that wish to solve an instance of the CSP problem.

# Acknowledgements

The author gratefully acknowledges the support of the EPSRC funded EP/L015692/1 STOR-i Centre for Doctoral Training. 

# References
