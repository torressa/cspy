import unittest

from numpy import array
from networkx import DiGraph

from cspy import BiDirectional


class TestsIssue69(unittest.TestCase):
    """
    Tests for issue #69
    https://github.com/torressa/cspy/issues/69
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [20, 30], [1, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", 3, res_cost=array([7, 13]), weight=3)
        self.G.add_edge(3, 0, res_cost=array([8, 10]), weight=4)
        self.G.add_edge(3, 6, res_cost=array([8, 3]), weight=7)
        self.G.add_edge(3, "Sink", res_cost=array([15, 12]), weight=1)
        self.G.add_edge(0, "Sink", res_cost=array([6, 3]), weight=7)
        self.G.add_edge(6, "Sink", res_cost=array([3, 8]), weight=8)
        # Expected results
        self.result_path = ['Source', 3, 6, 'Sink']
        self.total_cost = 18.0
        self.consumed_resources = [18.0, 24.0]

    def test_bidirectional(self):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        alg = BiDirectional(self.G, self.max_res, self.min_res)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertEqual(alg.consumed_resources, self.consumed_resources)

    def test_forward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='forward')
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_backward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='backward')
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)
