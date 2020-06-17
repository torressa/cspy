import sys
import unittest

from numpy import array
from networkx import DiGraph
from parameterized import parameterized

sys.path.append("../")

from cspy.algorithms.tabu import Tabu
from cspy.algorithms.bidirectional import BiDirectional


class TestsIssue20(unittest.TestCase):
    """
    Tests for issue #20
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

        self.max_res, self.min_res = [len(self.G.edges()), 2], [0, 0]

    @parameterized.expand(zip(range(100), range(100)))
    def testBiDirectionalRandom(self, _, seed):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                seed=seed,
                                elementary=True)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        # Check attributes
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testBiDirectionalGenerated(self):
        """
        Test BiDirectional with the search direction chosen by the number of
        direction with lowest number of generated labels.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="generated",
                                elementary=True)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        # Check attributes
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testBiDirectionalParallel(self):
        """
        Test BiDirectional with the parallel search
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                elementary=True)
        bidirec.run_parallel()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        # Check attributes
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testTabu(self):
        """
        Find shortest path of using Tabu
        """
        tabu = Tabu(self.G, self.max_res, self.min_res)
        tabu.run()
        path = tabu.path
        cost = tabu.total_cost
        total_res = tabu.consumed_resources
        # Check attributes
        self.assertEqual(cost, -5)
        self.assertTrue(all(total_res == [3, 2]))
        self.assertEqual(path, ['Source', 3, 2, 'Sink'])
        # Check path
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))


if __name__ == '__main__':
    unittest.main(TestsIssue20())
