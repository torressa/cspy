[![CircleCI](https://circleci.com/gh/torressa/cspy/tree/master.svg?style=svg&circle-token=910e28b03dd0d32967fae038a3cf28b6cdf56334)](https://circleci.com/gh/torressa/cspy/tree/master)
[![Documentation Status](https://readthedocs.org/projects/cspy/badge/?version=latest)](https://cspy.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/cspy.svg)](https://badge.fury.io/py/cspy)
[![codecov](https://codecov.io/gh/torressa/cspy/branch/master/graph/badge.svg?token=24tyrWinNT)](https://codecov.io/gh/torressa/cspy)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c28f50e92dae4bcc921f1bd142370608)](https://www.codacy.com/app/torressa/cspy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=torressa/cspy&amp;utm_campaign=Badge_Grade)
[![JOSS badge](https://joss.theoj.org/papers/25eda55801a528b982d03a6a61f7730d/status.svg)](https://joss.theoj.org/papers/25eda55801a528b982d03a6a61f7730d)
<!-- [![BCH compliance](https://bettercodehub.com/edge/badge/torressa/cspy?branch=master)](https://bettercodehub.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) -->

# cspy


A collection of algorithms for the (resource) Constrained Shortest Path (CSP) problem. 

The CSP problem was popularised by [Inrich and Desaulniers (2005)](@inrich). It was initially introduced as a subproblem for the bus driver scheduling problem, and has since then widely studied in a variety of different settings including: the vehicle routing problem with time windows (VRPTW), the technician routing and scheduling problem, the capacitated arc-routing problem, on-demand transportation systems, and, airport ground movement; among others.

More generally, in the applied column generation framework, particularly in the scheduling related literature, the CSP problem is commonly employed to generate columns.

Therefore, this library is of interest to the operational research community, students and academics alike, that wish to solve an instance of the CSP problem.

## Algorithms

Currently, the algorithms implemented include:

- [X] Monodirectional forward labeling algorithm;
- [X] Monodirectional backward labeling algorithm;
- [X] Bidirectional labeling algorithm with static halfway point;
- [X] Bidirectional labeling algorithm with dynamic halfway point [Tilk et al. (2017)](@tilk);
- [X] Heuristic Tabu search;
- [X] Greedy elimination procedure;
- [X] Greedy Randomised Adaptive Search Procedure (GRASP). Adapted from [Ferone et al. (2019)](@ferone);
- [X] Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology (PSOLGENT) [Marinakis et al. (2017)](@marinakis).

## Getting Started

### Prerequisites

Conceptual background and input formatting is discussed in the [docs](https://cspy.readthedocs.io/en/latest/how_to.html).

Module dependencies are:
- [NetworkX](https://networkx.github.io/documentation/stable/)
- [NumPy](https://docs.scipy.org/doc/numpy/reference/)

Note that [requirements.txt](requirements.txt) contains modules for development purposes.

### Installing

Installing the ``cspy`` package with ``pip`` should also install all the required packages. You can do this by running the following command in your terminal

```none
pip install cspy
```
or

```none
python3 -m pip install cspy
```

### Usage Examples

Please see the individual algorithms API Documentation for specific examples and more details:

- [Bidirectional and monodirectional algorithms](https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html)
- [Heuristic Tabu Search](https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html)
- [Greedy Elimination Procedure](https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html)
- [GRASP](https://cspy.readthedocs.io/en/latest/api/cspy.GRASP.html)
- [PSOLGENT](https://cspy.readthedocs.io/en/latest/api/cspy.PSOLGENT.html)

## Running the tests

To run the tests first, clone the repository into a path in your machine ``~/path/newfolder`` by running

```none
git clone https://github.com/torressa/cspy.git ~/path/newfolder
```

Then, go into the folder and run the tests using ``unittest``

```none
cd ~/path/newfolder
python3 -m unittest
```

Please make sure that the python package cspy is not already installed in your machine.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Contributing

### Issues

If you find a bug or there are some improvements you'd like to see (e.g. more algorithms), please raise a new issue with a clear explanation. 

See [feature_request.md](/.github/ISSUE_TEMPLATE/feature_request.md) for a template.

See [bug_report.md](/.github/ISSUE_TEMPLATE/bug_report.md) for a template.

### Contributing to the Software

When contributing to this repository, please first discuss the change you wish to make via an issue or email.
After that feel free to send a pull request.

#### Pull Request Process
 
 - If necessary, please perform documentation updates where appropriate (e.g. README.md, docs and [CHANGELOG.md](CHANGELOG.md)).
 - Increase the version numbers and reference the changes appropriately. Note that the versioning scheme used is based on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 - Wait for approval for merging.

### Seeking Support

If you have a question or need help, feel free to raise an issue explaining it.

Alternatively, email me at ``d.torressanchez@lancs.ac.uk``.

## Citing

If you'd like to cite this package, please use the following bib format:

```none
@Misc{cspy,
  author = {Torres Sanchez, David},
  title = {{\texttt{cspy}-- A Python package with a collection of algorithms for the (Resource) Constrained Shortest Path problem}},
  year = {2019},
  url = {\url{https://github.com/torressa/cspy}}
}
```

[@inrich]: https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints

[@tilk]: https://www.sciencedirect.com/science/article/pii/S0377221717302035

[@marinakis]: https://www.sciencedirect.com/science/article/pii/S0377221717302357

[@ferone]: https://www.tandfonline.com/doi/full/10.1080/10556788.2018.1548015