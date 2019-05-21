import sys
import time
import unittest
import networkx as nx
sys.path.append('../')
from cspy.label import Label
from cspy.algorithms import BiDirectional


class cspyTests(unittest.TestCase):
    ''' Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.'''

    def setUp(self):
        self.max_res, self.min_res = [4, 20], [3, 0]
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

    def testOutput(self):
        # Find shortest path of simple test digraph
        start = time.time()
        algObj = BiDirectional(self.G, self.max_res, self.min_res)
        path = algObj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])
        self.assertTrue(time.time() - start < 1)

    def testDominance(self):
        # Check whether forward and backward dominance makes sense
        L1 = Label(10, 'B', [6, 5], [])
        L2 = Label(1, 'C', [6, -3], [])
        L3 = Label(-10, 'Source', [3, -8.3], [])
        L4 = Label(-9, 'A', [4, -6.3], [])
        L5 = Label(0, 'Source', [4, -5.1], [])
        self.assertTrue(L2.dominates(L1))
        self.assertTrue(L3.dominates(L4))
        self.assertTrue(L3.dominates(L5))

    def testEmpty(self):
        # Check whether erratic graph raises exception
        self.assertRaises(Exception, BiDirectional, self.E,
                          self.max_res, self.min_res)

    def testNegativeEdges(self):
        # Check if negative resource costs work and whether
        # unreachable nodes are eliminated
        algObj = BiDirectional(self.H, [4, 20], [0, 0])
        path = algObj.run()
        # check if the unreachable node has been eliminated
        self.assertTrue('B' not in self.H.nodes())
        self.assertEqual(path, ['Source', 'A', 'C', 'D', 'Sink'])


if __name__ == '__main__':
    unittest.main()
