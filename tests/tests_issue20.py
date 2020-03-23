import sys
import unittest

from numpy import array
from networkx import DiGraph

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

    def testBiDirectional(self):
        """
        Find shortest path of simple test digraph using BiDirectional
        """
        bidirec = BiDirectional(self.G, self.max_res, self.min_res)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path
        self.assertEqual(path, ['Source', 2, 1, 'Sink'])
        # Check attributes
        self.assertEqual(cost, -10)
        self.assertTrue(all(total_res == [2, 1]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testTabu(self):
        """
        Find shortest path of simple test digraph using Tabu
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


if __name__ == '__main__':
    unittest.main(TestsIssue20())
