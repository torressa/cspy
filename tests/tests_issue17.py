import sys
import unittest

from networkx import DiGraph
from numpy import array

sys.path.append("../")
from cspy.algorithms.tabu import Tabu
from cspy.algorithms.label import Label
from cspy.algorithms.bidirectional import BiDirectional


class TestsIssue17(unittest.TestCase):
    """
    Tests for issue #17
    https://github.com/torressa/cspy/issues/17
    """
    def setUp(self):
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", 1, weight=3, res_cost=array([1, 1]))
        self.G.add_edge("Source", 2, weight=0, res_cost=array([1, 1]))
        self.G.add_edge(1, 2, weight=-1, res_cost=array([1, 1]))
        self.G.add_edge(1, 4, weight=5, res_cost=array([1, 1]))
        self.G.add_edge(2, 3, weight=3, res_cost=array([1, 1]))
        self.G.add_edge(3, 1, weight=1, res_cost=array([1, 1]))
        self.G.add_edge(2, 5, weight=-1, res_cost=array([1, 1]))
        self.G.add_edge(5, "Sink", weight=2, res_cost=array([1, 1]))
        self.G.add_edge(5, 4, weight=-1, res_cost=array([1, 1]))
        self.G.add_edge(4, 2, weight=3, res_cost=array([1, 1]))
        self.G.add_edge(4, "Sink", weight=3, res_cost=array([1, 1]))
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [len(self.G.edges()), 6], [0, 0]
        self.test_seed = 1000

    def testBiDirectionalBothDynamic(self):
        """
        Find shortest path of simple test digraph using the BiDirectional.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                seed=self.test_seed)
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'dynamic'
        self.assertRegex(cm.output[0], 'dynamic')

        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))
        self.assertEqual(self.max_res, [len(self.G.edges()), 6])
        self.assertEqual(self.min_res, [0, 0])

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
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))
        self.assertEqual(self.max_res, [len(self.G.edges()), 6])
        self.assertEqual(self.min_res, [0, 0])

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

        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))
        self.assertEqual(self.max_res, [len(self.G.edges()), 6])
        self.assertEqual(self.min_res, [0, 0])

    def testDominance(self):
        # Check forward and backward label dominance
        L1 = Label(0, 1, array([1, 1]), [])
        L2 = Label(-1, 1, array([1, 1]), [])
        L3 = Label(-10, 2, array([1, 1]), [])
        L4 = Label(-10, 2, array([0, 1]), [])
        L5 = Label(0, 2, array([1, 1]), [])
        self.assertTrue(L2.dominates(L1, "forward"))
        self.assertRaises(Exception, L1.dominates, L3)
        self.assertFalse(L3.dominates(L4, "forward"))
        self.assertTrue(L4.dominates(L3, "forward"))
        self.assertTrue(L3.dominates(L5, "forward"))
        # Test exception raiser for wrong direction
        self.assertRaises(Exception, L3.dominates, L5, "")

    def testTabu(self):
        tabu = Tabu(self.G, self.max_res, self.min_res)
        tabu.run()
        path = tabu.path
        cost_tabu = tabu.total_cost
        total_res = tabu.consumed_resources
        cost = sum([
            edge[2]['weight'] for edge in self.G.edges(data=True)
            if edge[0:2] in zip(path, path[1:])
        ])
        # Check new cost attribute
        self.assertEqual(cost, cost_tabu)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))
        self.assertEqual(self.max_res, [len(self.G.edges()), 6])
        self.assertEqual(self.min_res, [0, 0])

    def testInputExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.G, 'x', [1, 'foo'],
                          'up')


if __name__ == '__main__':
    unittest.main(TestsIssue17())
