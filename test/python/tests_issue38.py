from numpy import array
from networkx import DiGraph

from cspy.algorithms.bidirectional import BiDirectional

from utils import TestingBase


class TestsIssue38(TestingBase):
    """
    Tests for issue #38
    https://github.com/torressa/cspy/issues/38
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        # No resource costs required for custom REFs
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
        self.G.add_edge("A", "Sink", res_cost=array([1, 10]), weight=0)
        self.result_path = ["Source", "A", "Sink"]
        self.total_cost = 0
        self.consumed_resources = [2, 12]

    def test_bidirectional(self):
        alg = BiDirectional(self.G, self.max_res, self.min_res)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )
