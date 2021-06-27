import unittest

from numpy import array, testing
import numpy as np
from networkx import DiGraph

from cspy import PSOLGENT


class TestsIssue82(unittest.TestCase):
    """
    Tests for issue #82
    https://github.com/torressa/cspy/issues/82
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [10], [0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=1)
        self.G.add_edge("Source", 'A', res_cost=np.array([1]), weight=8)
        self.G.add_edge('A', 'B', res_cost=np.array([9]), weight=8)
        self.G.add_edge('A', 'Sink', res_cost=np.array([1]), weight=1)
        self.G.add_edge('Source', 'B', res_cost=np.array([1]), weight=1)
        self.G.add_edge('B', 'Sink', res_cost=np.array([10]), weight=1)
        self.G.add_edge('B', 'A', res_cost=np.array([1]), weight=1)
        # Expected CSP results
        self.result_path = ['Source', "B", "A", 'Sink']
        self.total_cost = 3.0
        self.consumed_resources = [3.0]

    def test_PSOLGENT(self):
        alg = PSOLGENT(self.G, self.max_res, self.min_res)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources,
                                    self.consumed_resources))
