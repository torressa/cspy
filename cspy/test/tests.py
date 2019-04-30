import time
import unittest
import networkx as nx
from cspy import algorithms as alg

# use python -m cspy.test.tests to run


class cspyTests(unittest.TestCase):
    ''' Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.'''

    def setUp(self):
        '''Create simple DiGraph'''
        self.G = nx.DiGraph(directed=True, n_res=2)
        self.L, self.U, self.run_time = 10, 30, 0

        self.G.add_edge('Source', 'A', res_cost=10, weight=0)
        self.G.add_edge('A', 'B', res_cost=10, weight=0)
        self.G.add_edge('A', 'C', res_cost=10, weight=0)
        self.G.add_edge('B', 'C', res_cost=10, weight=-1)
        self.G.add_edge('C', 'Sink', res_cost=10, weight=0)

    def testOutput(self):
        '''Find shortest path subject to resource constraints.'''
        start = time.time()
        path = alg.BiDirectional(self.G, self.L, self.U).run()
        self.run_time = time.time() - start
        self.assertIsInstance(path, list)

    def testRunningTime(self):
        self.assertTrue(self.run_time < 60)


if __name__ == '__main__':
    unittest.main()
