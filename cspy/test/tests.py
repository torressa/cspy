import sys
import time
import unittest
import networkx as nx
sys.path.append('../')
from cspy import label  # noqa
from cspy import algorithms as alg  # noqa


class cspyTests(unittest.TestCase):
    ''' Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.'''

    def setUp(self):
        '''Create simple DiGraph'''
        self.G = nx.DiGraph(directed=True, n_res=2)
        self.L, self.U, self.run_time = 1, 1.5, 0

        self.G.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
        self.G.add_edge('A', 'B', res_cost=[1, 0.3], weight=0)
        self.G.add_edge('A', 'C', res_cost=[1, 0.1], weight=0)
        self.G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
        self.G.add_edge('C', 'Sink', res_cost=[1, 10], weight=0)

    def testOutput(self):
        '''Find shortest path subject to resource constraints and store
        run time.'''
        start = time.time()
        path = alg.BiDirectional(self.G, self.L, self.U).run()
        self.run_time = time.time() - start
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testRunningTime(self):
        self.assertTrue(self.run_time < 60)

    def testDominance(self):
        L1 = label.Label(10, 'B', [6, 5], [])
        L2 = label.Label(0, 'C', [6, -3], [])
        self.assertTrue(L2.dominates(L1))


if __name__ == '__main__':
    unittest.main()
