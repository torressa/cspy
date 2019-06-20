"""TODO:
 -  write tests for Tabu algorithm
"""

import sys
import unittest
import networkx as nx
sys.path.append("../")
from cspy.algorithms.bidirectional import BiDirectional
from cspy.algorithms.tabu import Tabu
from cspy.label import Label


class TestsBasic(unittest.TestCase):
    """ Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm."""

    def setUp(self):
        self.max_res, self.min_res = [4, 20], [1, 0]
        # Create simple digraph to test algorithm
        self.G = nx.DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
        self.G.add_edge('A', 'B', res_cost=[1, 0.3], weight=0)
        self.G.add_edge('A', 'C', res_cost=[1, 0.1], weight=0)
        self.G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
        self.G.add_edge('C', 'Sink', res_cost=[1, 10], weight=0)

        # Create erratic digraph to test exception handling
        self.E = nx.DiGraph(directed=True)
        self.E.add_edge('Source', 'A', weight=0)

        # Create digraph with negative resource costs with unreachable node 'B'
        self.H = nx.DiGraph(directed=True, n_res=2)
        self.H.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
        self.H.add_edge('A', 'C', res_cost=[-1, 0.3], weight=0)
        self.H.add_edge('A', 'B', res_cost=[-1, 3], weight=0)
        self.H.add_edge('B', 'D', res_cost=[-1, 2], weight=0)
        self.H.add_edge('C', 'D', res_cost=[1, 0.1], weight=0)
        self.H.add_edge('D', 'Sink', res_cost=[1, 0.1], weight=0)

        self.J = nx.DiGraph(directed=True, n_res=2)
        self.J.add_edge('Source', 'A', res_cost=[1, 1], weight=1)
        self.J.add_edge('Source', 'B', res_cost=[1, 1], weight=1)
        self.J.add_edge('A', 'C', res_cost=[1, 1], weight=1)
        self.J.add_edge('B', 'C', res_cost=[2, 1], weight=-1)
        self.J.add_edge('C', 'D', res_cost=[1, 1], weight=-1)
        self.J.add_edge('D', 'E', res_cost=[1, 1], weight=1)
        self.J.add_edge('D', 'F', res_cost=[1, 1], weight=1)
        self.J.add_edge('F', 'Sink', res_cost=[1, 1], weight=1)
        self.J.add_edge('E', 'Sink', res_cost=[1, 1], weight=1)

    def testBothDirections(self):
        # Find shortest path of simple test digraph
        path = BiDirectional(self.G, self.max_res, self.min_res).run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testForward(self):
        # Find shortest path of simple test digraph
        path = BiDirectional(
            self.G, [200, 20], self.min_res, 'forward').run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testBackward(self):
        # Find shortest path of simple test digraph
        path = BiDirectional(self.G, self.max_res, [-1, 0], 'backward').run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testDominance(self):
        # Check whether forward and backward dominance makes sense
        L1 = Label(10, 'B', [6, 5], [])
        L2 = Label(1, 'B', [6, -3], [])
        L3 = Label(-10, 'A', [3, -8.3], [])
        L4 = Label(-9, 'A', [4, -6.3], [])
        L5 = Label(0, 'A', [4, -5.1], [])
        self.assertTrue(L2.dominates(L1))
        self.assertTrue(L3.dominates(L4))
        self.assertTrue(L3.dominates(L5))

    def testExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.E,
                          'x', [1], 'up')

    def testNegativeEdges(self):
        # Check if negative resource costs work and whether
        # unreachable nodes are eliminated
        path = BiDirectional(self.H, [5, 20], [0, 0]).run()
        # check if the unreachable node has been eliminated
        self.assertTrue('B' not in self.H.nodes())
        self.assertEqual(path, ['Source', 'A', 'C', 'D', 'Sink'])

    def testTabu(self):
        path = Tabu(self.J, [5, 5], [0, 0]).run()
        self.assertEqual(path, ['Source', 'A', 'C', 'D', 'E', 'Sink'])


if __name__ == '__main__':
    unittest.main()
