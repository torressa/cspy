# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## Fixed

- BiDirectional algorithm (#17).
- Heuristic used in Tabu for input in the networkx.astar_path algorithm (#20).

### Changed

- Documentation.
- BiDirectional algorithm:
	- Final label comparisons.
	- Seed handling for testing.
	- Renamed variables to avoid confusion.
	- Avoiding getting stuck processing cycles of input graphs.
	- Ensuring that edges in path correspond to an edge in the input graph.
	- Avoid overwriting inputs (`max_res` and `min_res`).
   	- Removed loops in `_get_next_label` and `_check_dominance` in favour of list comprehensions.
	- Use of `collections`.
	- logs for debugging in BiDirectional.
	- added `_save_current_best_label`.
	- Changed type of `self.finalLabel["direction"]` from list to `Label`. 

- Re-organised. Moved `label.py` and `path.py` into `algorithms/`.

## [0.0.10] - 09/02/2020

## Added

- PuLP example.

## Changed

- Documentation.
- Translated ``examples/cgar`` from gurobipy to pulp.
- CI build.

## [0.0.9] - 25/12/2019

## Added

- Added example directory with column generation example.
- Check for negative cost cycles.

### Changed

- PSOLGENT seed handling.
- Improved documentation.
- unit tests structure.

## [0.0.8] - 15/07/2019

### Added

- Generic resource extension functions options.

### Changed

- numpy.array integration.

## [0.0.5] - 9/07/2019

### Added

- `PSOLGENT`.
- `GreedyElim` simple test.

### Changed

- Fixed prune_graph preprocessing routine.
- YAPF google style.

## [0.0.3] - 9/07/2019

### Added

- `GRASP`.

### Changed

- Documentation updates.
- Updated README.
- Removed duplicate code in `tabu.py` and `greedy_elimination.py`.

## [0.0.1] - 1/07/2019

### Added

- assertLogs tests for bidirectional algorithm classification.
- Personal MIT LICENSE.
- `GreedyElim` Procedure.

### Changed

- Documentation updates.
- Docstring modifications to include maths.
- Updated README.

[unreleased]: https://github.com/torressa/cspy/compare/v0.0.10...HEAD
[0.0.10]: https://github.com/torressa/cspy/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/torressa/cspy/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/torressa/cspy/compare/0.0.5...v0.0.8
[0.0.5]: https://github.com/torressa/cspy/compare/0.0.3...0.0.5
[0.0.3]: https://github.com/torressa/cspy/compare/0.0.1...0.0.3
[0.0.1]: https://github.com/torressa/cspy/releases/tag/v0.0.1
