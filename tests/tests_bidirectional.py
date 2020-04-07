import sys
import unittest

from networkx import DiGraph
from numpy import array

sys.path.append("../")
from cspy.algorithms.bidirectional import BiDirectional
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

    def testBiDirectionalBothDynamic(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm with dynamic halfway point.
        """
        bidirec = BiDirectional(self.G, self.max_res, self.min_res)
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'dynamic'
        self.assertRegex(cm.output[0], 'dynamic')
        # Check exception for not running first
        with self.assertRaises(Exception) as context:
            bidirec.path
        self.assertTrue("run()" in str(context.exception))
        # Run and test results
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])
        self.assertEqual(cost, -13)
        self.assertTrue(all(total_res == [4, 15.3]))

    def testBiDirectionalForward(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm with only forward direction.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='forward')
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'forward'
        self.assertRegex(cm.output[0], 'forward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])
        self.assertEqual(cost, -13)
        self.assertTrue(all(total_res == [4, 15.3]))

    def testBiDirectionalBackward(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm with only backward direction.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='backward')
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'backward'
        self.assertRegex(cm.output[0], 'backward')
        # Check path
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])
        self.assertEqual(cost, -13)
        self.assertTrue(all(total_res == [4, 15.3]))

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
