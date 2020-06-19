import sys
import unittest

from networkx import DiGraph
from numpy import array

from parameterized import parameterized

sys.path.append("../")
from cspy.algorithms.tabu import Tabu
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
        self.max_res, self.min_res = [len(self.G.nodes()), 6], [0, 0]

    @parameterized.expand(zip(range(100), range(100)))
    def testBiDirectionalBothRandom(self, _, seed):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                seed=seed,
                                elementary=True)
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testBiDirectionalParallel(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                elementary=True)
        bidirec.run_parallel()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testBiDirectionalForward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='forward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testBiDirectionalBackward(self):
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                direction='backward')
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        # Check path and other attributes
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertEqual(cost, 1)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testTabu(self):
        tabu = Tabu(self.G, self.max_res, self.min_res)
        tabu.run()
        path = tabu.path
        cost_tabu = tabu.total_cost
        total_res = tabu.consumed_resources
        cost = sum(edge[2]['weight']
                   for edge in self.G.edges(data=True)
                   if edge[0:2] in zip(path, path[1:]))
        # Check new cost attribute
        self.assertEqual(cost, cost_tabu)
        self.assertTrue(all(total_res == [3, 3]))
        self.assertEqual(path, ['Source', 2, 5, 'Sink'])
        self.assertTrue(all(e in self.G.edges() for e in zip(path, path[1:])))

    def testInputExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.G, 'x', [1, 'foo'],
                          'up')


if __name__ == '__main__':
    unittest.main(TestsIssue17())
