from numpy import array
from networkx import DiGraph

from cspy import PSOLGENT

from utils import TestingBase


class TestsIssue82(TestingBase):
    """
    Tests for issue #82
    https://github.com/torressa/cspy/issues/82
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [10], [0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=1)
        self.G.add_edge("Source", "A", res_cost=array([1]), weight=8)
        self.G.add_edge("A", "B", res_cost=array([9]), weight=8)
        self.G.add_edge("A", "Sink", res_cost=array([1]), weight=1)
        self.G.add_edge("Source", "B", res_cost=array([1]), weight=1)
        self.G.add_edge("B", "Sink", res_cost=array([10]), weight=1)
        self.G.add_edge("B", "A", res_cost=array([1]), weight=1)
        # Expected CSP results
        self.result_path = ["Source", "B", "A", "Sink"]
        self.total_cost = 3.0
        self.consumed_resources = [3.0]

    def test_PSOLGENT(self):
        alg = PSOLGENT(self.G, self.max_res, self.min_res)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )
