| OS     | C++ | Python |
|:-------|-----|--------|
| Linux  | [![Status][cpp_linux_svg]][cpp_linux_link] | [![Status][python_linux_svg]][python_linux_link] |
| macOS  | [![Status][cpp_osx_svg]][cpp_osx_link] | [![Status][python_osx_svg]][python_osx_link] |
| Windows  | [![Status][cpp_win_svg]][cpp_win_link] | [![Status][python_win_svg]][python_win_link] |


[cpp_linux_svg]: https://github.com/torressa/cspy/workflows/Ubuntu%20Cpp/badge.svg
[cpp_linux_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22Ubuntu+Cpp%22
[python_linux_svg]: https://github.com/torressa/cspy/workflows/Ubuntu%20Python/badge.svg
[python_linux_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22Ubuntu+Python%22

[cpp_osx_svg]: https://github.com/torressa/cspy/workflows/MacOS%20Cpp/badge.svg
[cpp_osx_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22MacOS+Cpp%22
[python_osx_svg]: https://github.com/torressa/cspy/workflows/MacOS%20Python/badge.svg
[python_osx_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22MacOS+Python%22

[cpp_win_svg]: https://github.com/torressa/cspy/workflows/Windows%20Cpp/badge.svg
[cpp_win_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22Windows+Cpp%22
[python_win_svg]: https://github.com/torressa/cspy/workflows/Windows%20Python/badge.svg
[python_win_link]: https://github.com/torressa/cspy/actions?query=workflow%3A%22Windows+Python%22

[![Documentation Status](https://readthedocs.org/projects/cspy/badge/?version=latest)](https://cspy.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/cspy.svg)](https://badge.fury.io/py/cspy)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c28f50e92dae4bcc921f1bd142370608)](https://www.codacy.com/app/torressa/cspy?utm_source=github.com&utm_medium=referral&utm_content=torressa/cspy&utm_campaign=Badge_Grade)
[![JOSS badge](https://joss.theoj.org/papers/25eda55801a528b982d03a6a61f7730d/status.svg)](https://joss.theoj.org/papers/25eda55801a528b982d03a6a61f7730d)


# cspy

A collection of algorithms for the (resource) Constrained Shortest Path (CSP) problem.

The CSP problem was popularised by [Inrich and Desaulniers (2005)](https://www.researchgate.net/publication/227142556_Shortest_Path_Problems_with_Resource_Constraints). It was initially introduced as a subproblem for the bus driver scheduling problem, and has since then widely studied in a variety of different settings including: the vehicle routing problem with time windows (VRPTW), the technician routing and scheduling problem, the capacitated arc-routing problem, on-demand transportation systems, and, airport ground movement; among others.

More generally, in the applied column generation framework, particularly in the scheduling related literature, the CSP problem is commonly employed to generate columns.

Therefore, this library is of interest to the operational research community, students and academics alike, that wish to solve an instance of the CSP problem.

## Algorithms

Currently, the exact and metaheuristic algorithms implemented include:

- [x] Monodirectional forward labeling algorithm (exact);
- [x] Monodirectional backward labeling algorithm (exact);
- [x] Bidirectional labeling algorithm with dynamic halfway point (exact) [Tilk et al. (2017)](https://www.sciencedirect.com/science/article/pii/S0377221717302035);
- [x] Heuristic Tabu search (metaheuristic);
- [x] Greedy elimination procedure (metaheuristic);
- [x] Greedy Randomised Adaptive Search Procedure (GRASP) (metaheuristic). Adapted from [Ferone et al. (2019)](https://www.tandfonline.com/doi/full/10.1080/10556788.2018.1548015);
- [x] Particle Swarm Optimization with combined Local and Global Expanding Neighborhood Topology (PSOLGENT) (metaheuristic) [Marinakis et al. (2017)](https://www.sciencedirect.com/science/article/pii/S0377221717302357).

Please see the individual algorithms API Documentation for some toy examples and more details:

- [Bidirectional and monodirectional algorithms](https://cspy.readthedocs.io/en/latest/api/cspy.BiDirectional.html)
- [Heuristic Tabu Search](https://cspy.readthedocs.io/en/latest/api/cspy.Tabu.html)
- [Greedy Elimination Procedure](https://cspy.readthedocs.io/en/latest/api/cspy.GreedyElim.html)
- [GRASP](https://cspy.readthedocs.io/en/latest/api/cspy.GRASP.html)
- [PSOLGENT](https://cspy.readthedocs.io/en/latest/api/cspy.PSOLGENT.html)
## Getting Started

### Prerequisites

Conceptual background and input formatting is discussed in the [docs](https://cspy.readthedocs.io/en/latest/how_to.html).

Module dependencies are:

- [NetworkX](https://networkx.github.io/documentation/stable/)
- [NumPy](https://docs.scipy.org/doc/numpy/reference/)

Note that [requirements.txt](requirements.txt) contains modules for development purposes.

### Installing

Installing the `cspy` package with `pip` should also install all the required packages. You can do this by running the following command in your terminal

```none
pip install cspy
```

or

```none
python3 -m pip install cspy
```

### Quick start

#### Python

```python
# Imports
from cspy import BiDirectional
from networkx import DiGraph
from numpy import array

max_res, min_res = [4, 20], [1, 0]
# Create a DiGraph
G = DiGraph(directed=True, n_res=2)
G.add_edge("Source", "A", res_cost=[1, 2], weight=0)
G.add_edge("A", "B", res_cost=[1, 0.3], weight=0)
G.add_edge("A", "C", res_cost=[1, 0.1], weight=0)
G.add_edge("B", "C", res_cost=[1, 3], weight=-10)
G.add_edge("B", "Sink", res_cost=[1, 2], weight=10)
G.add_edge("C", "Sink", res_cost=[1, 10], weight=0)

# init algorithm
bidirec = BiDirectional(G, max_res, min_res)

# Call and query attributes
bidirec.run()
print(bidirec.path)
print(bidirec.total_cost)
print(bidirec.consumed_resources)
```

#### Cpp

```cpp
#include "bidirectional.h"

namespace bidirectional {

void wrap() {
  // Init
  const std::vector<double> max_res         = {4.0, 20.0};
  const std::vector<double> min_res         = {1.0, 0.0};
  const int                 number_vertices = 5;
  const int                 number_edges    = 5;
  auto                      bidirectional   = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);

  // Populate graph
  bidirectional->addEdge("Source", "A", 0, {1, 2});
  bidirectional->addEdge("A", "B", 0, {1, 0.3});
  bidirectional->addEdge("B", "C", -10, {1, 3});
  bidirectional->addEdge("B", "Sink", 10, {1, 2});
  bidirectional->addEdge("C", "Sink", 0, {1, 10});

  // Run and query attributes
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();
}

} // namespace bidirectional
```

### Examples

- [`vrpy`](https://github.com/Kuifje02/vrpy) : External vehicle routing framework which uses `cspy` to solve different variants of the vehicle routing problem using column generation. Particulatly, see  [`subproblem_cspy.py`](https://github.com/Kuifje02/vrpy/blob/master/vrpy/subproblem_cspy.py).
- [`cgar`](examples/cgar) : [needs revising] Complex example use of `cspy` in a column generation example applied to the aircraft recovery problem.
- [`jpath`](examples/jpath) : Simple example showing the necessary graph adptations and the use of custom resource extension functions.


## Running the tests

### Prerequisites

- Docker, docker-compose

To run the tests first, clone the repository into a path in your machine `~/path/newfolder` by running

```none
git clone https://github.com/torressa/cspy.git ~/path/newfolder
```
### Running the Cpp tests

```
cd ~/path/newfolder/tools/dev
./build
```

### Running the Python tests

```
cd ~/path/newfolder/tools/dev
./build -c -p
```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Contributing

### Issues

If you find a bug or there are some improvements you'd like to see (e.g. more algorithms), please raise a new issue with a clear explanation.

### Contributing to the Software

When contributing to this repository, please first discuss the change you wish to make via an issue or email.
After that feel free to send a pull request.

#### Pull Request Process

- If necessary, please perform documentation updates where appropriate (e.g. README.md, docs and [CHANGELOG.md](CHANGELOG.md)).
- Increase the version numbers and reference the changes appropriately. Note that the versioning scheme used is based on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
- Wait for approval for merging.

### Seeking Support

If you have a question or need help, feel free to raise an issue explaining it.

Alternatively, email me at `d.torressanchez@lancaster.ac.uk`.

## Citing

If you'd like to cite this package, please use the following bib format:

```none
@article{torressa2020,
  doi = {10.21105/joss.01655},
  url = {https://doi.org/10.21105/joss.01655},
  year = {2020},
  publisher = {The Open Journal},
  volume = {5},
  number = {49},
  pages = {1655},
  author = {{Torres Sanchez}, David},
  title = {cspy: A Python package with a collection of algorithms for the (Resource) Constrained Shortest Path problem},
  journal = {Journal of Open Source Software}
}
```
