import unittest

from networkx import DiGraph
from numpy import array
from parameterized import parameterized

from cspy.algorithms.bidirectional import BiDirectional
from cspy.algorithms.label import Label


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

    @parameterized.expand(zip(range(100), range(100)))
    def testBiDirectionalBothRandom(self, _, seed):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="random",
                                seed=seed)
        # Run and test results
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'C', 'Sink'])
        self.assertEqual(cost, 20)
        self.assertTrue(all(total_res == [3, 3]))

    #  FIXME
    # def testBiDirectionalParallel(self):
    #     bidirec = BiDirectional(self.G, self.max_res, self.min_res)
    #     # Run and test results
    #     bidirec.run_parallel()
    #     path = bidirec.path
    #     cost = bidirec.total_cost
    #     total_res = bidirec.consumed_resources
    #     self.assertEqual(path, ['Source', 'A', 'C', 'Sink'])
    #     self.assertEqual(cost, 20)
    #     self.assertTrue(all(total_res == [3, 3]))

    def testBiDirectionalForward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='forward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'C', 'Sink'])
        self.assertEqual(cost, 20)
        self.assertTrue(all(total_res == [3, 3]))

    def testBiDirectionalBackward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='backward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'C', 'Sink'])
        self.assertEqual(cost, 20)
        self.assertTrue(all(total_res == [3, 3]))


if __name__ == '__main__':
    unittest.main(TestsIssue41())
