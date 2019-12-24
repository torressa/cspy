import sys
import unittest

from networkx import DiGraph
from numpy import array

sys.path.append("../")
from cspy.algorithms.bidirectional import BiDirectional
from cspy.label import Label


class TestsBiDirectional(unittest.TestCase):
    """ Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm."""

    def setUp(self):
        self.max_res, self.min_res = [4, 20], [1, 0]
        # Create simple digraph to test algorithm
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=array([1, 2]), weight=-1)
        self.G.add_edge('A', 'B', res_cost=array([1, 0.3]), weight=-1)
        # self.G.add_edge('A', 'C', res_cost=[1, 0.1], weight=1)
        self.G.add_edge('B', 'C', res_cost=array([1, 3]), weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=array([1, 2]), weight=10)
        self.G.add_edge('C', 'Sink', res_cost=array([1, 10]), weight=-1)

    def testBiDirectionalBoth(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(self.G, self.max_res, self.min_res)
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm(U=self.max_res[0], L=self.min_res[0])
        self.assertRegex(cm.output[0], 'dynamic')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testBiDirectionalForward(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(self.G, [200, 20],
                                self.min_res,
                                direction='forward')
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm()
        self.assertRegex(cm.output[0], 'forward')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testBiDirectionalBackward(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(self.G,
                                self.max_res, [-1, 0],
                                direction='backward')
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm()
        self.assertRegex(cm.output[0], 'backward')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testDominance(self):
        # Check forward and backward dominance
        L1 = Label(10, 'B', array([6, 5]), [])
        L2 = Label(1, 'B', array([6, -3]), [])
        L3 = Label(-10, 'A', array([3, -8.3]), [])
        L4 = Label(-9, 'A', array([4, -6.3]), [])
        L5 = Label(0, 'A', array([4, -5.1]), [])
        self.assertTrue(L2.dominates(L1))
        self.assertTrue(L3.dominates(L4))
        self.assertTrue(L3.dominates(L5))

    def testInputExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.G, 'x', [1, 'foo'],
                          'up')


if __name__ == '__main__':
    unittest.main()
