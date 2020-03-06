import sys
import unittest

from numpy import array
from networkx import DiGraph

sys.path.append("../")
from cspy.algorithms.tabu import Tabu


class TestsIssue19(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    Includes algorithm classification, and some exception handling.
    """

    def setUp(self):
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", 1, weight=10, res_cost=array([1, 1]))
        self.G.add_edge("Source", 2, weight=10, res_cost=array([1, 1]))
        self.G.add_edge("Source", 3, weight=10, res_cost=array([1, 1]))
        self.G.add_edge(1, "Sink", weight=-10, res_cost=array([1, 0]))
        self.G.add_edge(2, "Sink", weight=-10, res_cost=array([1, 0]))
        self.G.add_edge(3, "Sink", weight=-10, res_cost=array([1, 0]))
        self.G.add_edge(3, 2, weight=-5, res_cost=array([1, 1]))
        self.G.add_edge(2, 1, weight=-10, res_cost=array([1, 1]))

        self.max_res, self.min_res = [len(self.G.edges()), 2], [0, 0]

    def testTabu(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm with dynamic halfway point.
        """
        path = Tabu(self.G, self.max_res, self.min_res).run()
        self.assertEqual(path, ['Source', 1, 'Sink'])
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))


if __name__ == '__main__':
    unittest.main()
