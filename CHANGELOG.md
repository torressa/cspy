# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [v0.1.1] - 21/05/2020

### Changed
- BiDirectional:
  - Reverted backward REF as it is required for some problems.
  - Added REF join parameter that is required when joining forward and backward labels using custom REFs.
- Moved notes and examples from docstrings to the docs folder. 
- Final JOSS paper changes

## [v0.1.0] - 14/04/2020

### Added 

- BiDirectional:
  - Option to chose method for direction selection.
- [vrpy](https://github.com/Kuifje02/vrpy) submodule.

### Changed 

- BiDirectional:
  - Label storage, divided into unprocessed, generated and non-dominated labels
  - Restricted join algorithm to non-dominated label
  - Changed backward resource extensions to avoid complex and computationally costly inversion. Additionally, it removes the requirement of an explicit backward REF.
  - Filtering for backward labels in join algorithm.
  - Cleaned up unused label operator overloads.
  - Removed costly comparison in `_propagate_label`.
  - Changed generated labels attributes from dict of deques to dict of int with count.

- Rework of path and algorithm attributes to avoid duplication
- Replaced `networkx.astar` algorithm with a procedure that finds a short simple
path using `networkx.shortest_simple_paths`.

### Removed

- Negative edge cycle assumption

## [v0.0.14] - 01/04/2020

### Removed

- Bidirectional
  - Removed use of halway point filtering for labels

## [v0.0.13] - 26/03/2020

### Added

- Included dev requirements file with new package for testing and examples requirements.

### Changed

- BiDirectional algorithm:
  - Resource based comparisons for label extension
  - Simplified attributes.
  - Implemented full path joining procedure from [Righini and Salani (2006)](https://www.sciencedirect.com/science/article/pii/S1572528606000417).
  - Rectified half-way check.
- parameterized some tests.

## [v0.0.12] - 14/03/2020

### Changed

- Documentation.
- BiDirectional algorithm:
  - **Removed** termination criteria.
  - Implemented half way procedure from [Righini and Salani (2006)](https://www.sciencedirect.com/science/article/pii/S1572528606000417) in `self._half_way` (Closes #21).
  - Changed label dominance to an equivalent but more elegant function.
  - Changed final label saving to account for when neither of two labels dominate.
- Backwards incompatible path, cost and total_resource feature.
- Preprocessing functions.

## [v0.0.11] - 06/03/2020

## Fixed

- BiDirectional algorithm: returning path with edge not in graph (Closes #17 :pray:).
- Heuristic used in Tabu for input in the networkx.astar_path algorithm (Closes #20).

### Changed

- Documentation.
- BiDirectional algorithm:

  - Final label comparisons.
  - Seed handling for testing.
  - Renamed variables to avoid confusion. - Avoiding getting stuck processing cycles of input graphs. - Ensuring that edges in path correspond to an edge in the input graph. - Avoid overwriting inputs (`max_res` and `min_res`). - Removed loops in `_get_next_label` and `_check_dominance` in favour of list comprehensions. - Use of `collections`. - logs for debugging in BiDirectional.
  - added `_save_current_best_label`.
  - Changed type of `self.finalLabel["direction"]` from list to `Label`.

- Re-organised. Moved `label.py` and `path.py` into `algorithms/`.

## [v0.0.10] - 09/02/2020

## Added

- PuLP example.

## Changed

- Documentation.
- Translated `examples/cgar` from gurobipy to pulp.
- CI build.

## [v0.0.9] - 25/12/2019

## Added

- Added example directory with column generation example.
- Check for negative cost cycles.

### Changed

- PSOLGENT seed handling.
- Improved documentation.
- unit tests structure.

## [v0.0.8] - 15/07/2019

### Added

- Generic resource extension functions options.

### Changed

- numpy.array integration.

## [v0.0.5] - 9/07/2019

### Added

- `PSOLGENT`.
- `GreedyElim` simple test.

### Changed

- Fixed prune_graph preprocessing routine.
- YAPF google style.

## [v0.0.3] - 9/07/2019

### Added

- `GRASP`.

### Changed

- Documentation updates.
- Updated README.
- Removed duplicate code in `tabu.py` and `greedy_elimination.py`.

## [v0.0.1] - 1/07/2019

### Added

- assertLogs tests for bidirectional algorithm classification.
- Personal MIT LICENSE.
- `GreedyElim` Procedure.

### Changed

- Documentation updates.
- Docstring modifications to include maths.
- Updated README.

[unreleased]: https://github.com/torressa/cspy/compare/v0.1.1...HEAD
[v0.1.1]: https://github.com/torressa/cspy/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/torressa/cspy/compare/v0.0.14...v0.1.0
[v0.0.14]: https://github.com/torressa/cspy/compare/v0.0.13...v0.0.14
[v0.0.13]: https://github.com/torressa/cspy/compare/v0.0.12...v0.0.13
[v0.0.12]: https://github.com/torressa/cspy/compare/v0.0.11...v0.0.12
[v0.0.11]: https://github.com/torressa/cspy/compare/v0.0.10...v0.0.11
[v0.0.11]: https://github.com/torressa/cspy/compare/v0.0.10...v0.0.11
[v0.0.10]: https://github.com/torressa/cspy/compare/v0.0.9...v0.0.10
[v0.0.9]: https://github.com/torressa/cspy/compare/v0.0.8...v0.0.9
[v0.0.8]: https://github.com/torressa/cspy/compare/0.0.5...v0.0.8
[v0.0.5]: https://github.com/torressa/cspy/compare/0.0.3...0.0.5
[v0.0.3]: https://github.com/torressa/cspy/compare/0.0.1...0.0.3
[v0.0.1]: https://github.com/torressa/cspy/releases/tag/v0.0.1
