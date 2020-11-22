import unittest

from numpy import array
from networkx import DiGraph
from parameterized import parameterized

from cspy.algorithms.bidirectional import BiDirectional


class TestsIssue25(unittest.TestCase):
    """
    Tests for issue #25
    https://github.com/torressa/cspy/issues/25
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
        # Expected results
        self.result_path = ['Source', 'A', 'B', 'C', 'Sink']
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    @parameterized.expand(zip(range(1), range(1)))
    def test_bidirectional_random(self, _, seed):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="random",
                            seed=seed,
                            elementary=True)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)
