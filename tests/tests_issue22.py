import sys
import unittest

from numpy import array
from random import randint
from networkx import DiGraph, astar_path

sys.path.append("../")
from cspy.algorithms.tabu import Tabu
from cspy.algorithms.label import Label
from cspy.algorithms.bidirectional import BiDirectional


class TestsIssue22(unittest.TestCase):
    """
    Tests for issue #22
    https://github.com/torressa/cspy/issues/22
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
        self.test_seed = randint(1000, 10000000)

    def testDominance(self):
        # Check forward and backward label dominance
        L1 = Label(-10, "Sink", array([3, 0]), [])
        L2 = Label(0, "Sink", array([1, 0]), [])

        self.assertFalse(L1.dominates(L2, "forward"))
        self.assertFalse(L2.dominates(L1, "forward"))
        self.assertTrue(L1.dominates(L2, "backward"))
        self.assertFalse(L2.dominates(L1, "backward"))

        if not L1.dominates(L2, "forward") and not L2.dominates(L1, "forward"):
            self.assertTrue(L1.dominates(L2, "backward"))

    def testTabu(self):
        """
        Find shortest path of simple test digraph using Tabu.
        """
        tabu = Tabu(self.G, self.max_res, self.min_res)
        tabu.run()
        path = tabu.path
        cost = tabu.total_cost
        total_res = tabu.consumed_resources
        # Check attributes
        self.assertEqual(cost, 0)
        self.assertTrue(all(total_res == [2, 1]))
        # Check path
        self.assertEqual(path, ['Source', 1, 'Sink'])
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))
        # Check if networkx's astar_path gives the same path
        path_star = astar_path(self.G, "Source", "Sink")
        self.assertEqual(path_star, ['Source', 1, 'Sink'])

    def testBiDirectionalBothDynamic(self):
        """
        Find shortest path of simple test digraph using BiDirectional.
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
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))

    def testBiDirectionalForward(self):
        """
        Find shortest path of simple test digraph using BiDirectional
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
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))

    def testBiDirectionalBackward(self):
        """
        Find shortest path of simple test digraph using BiDirectional
        algorithm with only backward direction.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='backward')
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'forward'
        self.assertRegex(cm.output[0], 'backward')

        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [3, 2]))


if __name__ == '__main__':
    unittest.main(TestsIssue22())
