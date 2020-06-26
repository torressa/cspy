import unittest

from networkx import DiGraph
from numpy import array
from parameterized import parameterized

from cspy import BiDirectional
from cspy.algorithms.label import Label


class TestsBiDirectional(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    Includes algorithm classification, and some exception handling.
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

        self.result_path = ['Source', 'A', 'B', 'C', 'Sink']
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    @parameterized.expand(zip(range(100), range(100)))
    def testBothRandom(self, _, seed):
        bidirec = BiDirectional(self.G, self.max_res, self.min_res, seed=96)
        # Run and test results
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothGenerated(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="generated")
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothProcessed(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="processed")
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothUnprocessed(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="unprocessed")
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothUnprocessedTimelimit(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="unprocessed",
                                time_limit=1)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothUnprocessedThreshold(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm with unprocessed guided search
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="unprocessed",
                                threshold=0)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothUnprocessedTimelimitThreshold(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="unprocessed",
                                time_limit=1,
                                threshold=0)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBothUnprocessedTimelimitRaises(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                method="unprocessed",
                                time_limit=0)
        self.assertRaises(Exception, bidirec.run)

    def testParallel(self):
        bidirec = BiDirectional(self.G, self.max_res, self.min_res)
        # Run and test results
        bidirec.run_parallel()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testParallelThreshold(self):
        bidirec = BiDirectional(self.G, self.max_res, self.min_res, threshold=0)
        # Run and test results
        bidirec.run_parallel()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testParallelTimeLimit(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                threshold=0,
                                time_limit=0)
        # Run and test results
        self.assertRaises(Exception, bidirec.run_parallel)

    def testForward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='forward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testBackward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='backward')
        # Check path
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(all(total_res == self.consumed_resources))

    def testDominance(self):
        # Check forward and backward label dominance
        L1 = Label(10, 'B', array([6, 5]), [])
        L2 = Label(1, 'B', array([6, -3]), [])
        L3 = Label(-10, 'A', array([3, -8]), [])
        L4 = Label(-10, 'A', array([4, -6]), [])
        self.assertTrue(L2.dominates(L1, "forward"))
        self.assertTrue(L3.dominates(L4, "forward"))

    def testInputExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.G, 'x', [1, 'foo'],
                          'up')


if __name__ == '__main__':
    unittest.main(TestsBiDirectional())
