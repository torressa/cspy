import unittest
from time import time

from networkx import DiGraph
from numpy import array
from parameterized import parameterized

from cspy import GreedyElim


class TestsGreedyElimination(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    Includes algorithm classification, and some exception handling.
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=array([1, 2]), weight=-1)
        self.G.add_edge('A', 'B', res_cost=array([1, 0.3]), weight=-1)
        self.G.add_edge('B', 'C', res_cost=array([1, 3]), weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=array([1, 2]), weight=10)
        self.G.add_edge('C', 'Sink', res_cost=array([1, 10]), weight=-1)

        self.result_path = ['Source', 'A', 'B', 'C', 'Sink']
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    def testSimple(self):
        alg = GreedyElim(self.G, self.max_res, self.min_res)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def testAstar(self):
        alg = GreedyElim(self.G, self.max_res, self.min_res, algorithm="astar")
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def testTimelimit(self):
        alg = GreedyElim(self.G, self.max_res, self.min_res, time_limit=0.001)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def testThreshold(self):
        alg = GreedyElim(self.G, self.max_res, self.min_res, threshold=100)
        alg.run()
        self.assertEqual(alg.path, ["Source", "A", "B", "Sink"])
        self.assertEqual(alg.total_cost, 8)
        self.assertTrue(all(alg.consumed_resources == [3, 4.3]))

    def testTimelimitThreshold(self):
        alg = GreedyElim(self.G,
                         self.max_res,
                         self.min_res,
                         time_limit=0.001,
                         threshold=0)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def testTimelimitRaises(self):
        alg = GreedyElim(self.G, self.max_res, self.min_res, time_limit=0)
        self.assertRaises(Exception, alg.run)


if __name__ == '__main__':
    unittest.main(TestsGreedyElimination())
