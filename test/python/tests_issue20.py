from numpy import array
from networkx import DiGraph

from cspy.algorithms.tabu import Tabu
from cspy.algorithms.bidirectional import BiDirectional

from utils import TestingBase


class TestsIssue20(TestingBase):
    """Tests for issue #20
    https://github.com/torressa/cspy/issues/20
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
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [len(self.G.edges()), 2], [0, 0]
        # Expected results
        self.result_path = ["Source", 2, 1, "Sink"]
        self.total_cost = -10
        self.consumed_resources = [3, 2]

    def test_bidirectional(self):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        alg = BiDirectional(self.G, self.max_res, self.min_res, elementary=True)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )
        self.assertTrue(all(e in self.G.edges() for e in zip(alg.path, alg.path[1:])))

    def test_tabu(self):
        """
        Find shortest path of using Tabu
        """
        alg = Tabu(self.G, self.max_res, self.min_res)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )
        self.assertTrue(all(e in self.G.edges() for e in zip(alg.path, alg.path[1:])))
