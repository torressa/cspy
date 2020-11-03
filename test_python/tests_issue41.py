import unittest

from numpy import array
from networkx import DiGraph
from parameterized import parameterized

from cspy import BiDirectional


class TestsIssue41(unittest.TestCase):
    """
    Tests for issue #41
    https://github.com/torressa/cspy/issues/41
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [3, 3], [0, 3]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 1]), weight=10)
        self.G.add_edge("A", "B", res_cost=array([1, 0]), weight=3)
        self.G.add_edge("A", "C", res_cost=array([1, 1]), weight=10)
        self.G.add_edge("B", "C", res_cost=array([1, 0]), weight=3)
        self.G.add_edge("B", "Sink", res_cost=array([1, 1]), weight=5)
        self.G.add_edge("C", "Sink", res_cost=array([1, 1]), weight=0)
        # Expected results
        self.result_path = ['Source', 'A', 'C', 'Sink']
        self.total_cost = 20
        self.consumed_resources = [3, 3]

    @parameterized.expand(zip(range(100), range(100)))
    def test_bidirectional_random(self, _, seed):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="random",
                            seed=seed)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def test_bidirectional_forward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='forward')
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def test_bidirectional_backward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='backward')
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))
