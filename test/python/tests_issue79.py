import unittest

from numpy import array
from networkx import DiGraph

from cspy import PSOLGENT


class TestsIssue79(unittest.TestCase):
    """
    Tests for issue #79
    https://github.com/torressa/cspy/issues/79
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [7, 5], [1, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", '1', res_cost=array([5, 3]), weight=1)
        self.G.add_edge("Source", '2', res_cost=array([1, 1]), weight=2)
        self.G.add_edge('1', "Sink", res_cost=array([5, 3]), weight=1)
        self.G.add_edge('2', "Sink", res_cost=array([1, 1]), weight=2)
        self.G.add_edge("Source", "Sink", res_cost=array([2, 2]), weight=3)
        # Expected results
        self.result_path = ['Source', 'Sink']
        self.total_cost = 3.0
        self.consumed_resources = [2.0, 2.0]

    def test_bidirectional(self):
        """
        Test PSOLGENT can find path of Source directly connected to Sink
        """
        alg = PSOLGENT(self.G, self.max_res, self.min_res)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertEqual(alg.consumed_resources, self.consumed_resources)
