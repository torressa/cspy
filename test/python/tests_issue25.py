from numpy import array
from networkx import DiGraph

from cspy.algorithms.bidirectional import BiDirectional

from utils import TestingBase


class TestsIssue25(TestingBase):
    """
    Tests for issue #25
    https://github.com/torressa/cspy/issues/25
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 2]), weight=-1)
        self.G.add_edge("A", "B", res_cost=array([1, 0.3]), weight=-1)
        self.G.add_edge("B", "C", res_cost=array([1, 3]), weight=-10)
        self.G.add_edge("B", "Sink", res_cost=array([1, 2]), weight=10)
        self.G.add_edge("C", "Sink", res_cost=array([1, 10]), weight=-1)
        # Expected results
        self.result_path = ["Source", "A", "B", "C", "Sink"]
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    def test_bidirectional(self):
        alg = BiDirectional(self.G, self.max_res, self.min_res, elementary=True)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )
