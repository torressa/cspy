
import sys
import unittest
from networkx import DiGraph
sys.path.append("../")
from cspy.algorithms.bidirectional import BiDirectional
from cspy.algorithms.tabu import Tabu
from cspy.algorithms.greedy_elimination import GreedyElim
from cspy.algorithms.grasp import GRASP

from cspy.label import Label


class TestsBasic(unittest.TestCase):
    """ Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm."""

    def setUp(self):
        self.max_res, self.min_res = [4, 20], [1, 0]
        # Create simple digraph to test algorithm
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=[1, 2], weight=-1)
        self.G.add_edge('A', 'B', res_cost=[1, 0.3], weight=-1)
        # self.G.add_edge('A', 'C', res_cost=[1, 0.1], weight=1)
        self.G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
        self.G.add_edge('C', 'Sink', res_cost=[1, 10], weight=-1)

        # Create erratic digraph to test exception handling
        self.E = DiGraph(directed=True)
        self.E.add_edge('Source', 'A')

        # Create digraph with negative resource costs with unreachable node 'B'
        self.H = DiGraph(directed=True, n_res=2)
        self.H.add_edge('Source', 'A', res_cost=[1, 2], weight=0)
        self.H.add_edge('A', 'C', res_cost=[-1, 0.3], weight=0)
        self.H.add_edge('A', 'B', res_cost=[-1, 3], weight=0)
        self.H.add_edge('B', 'D', res_cost=[-1, 2], weight=0)
        self.H.add_edge('C', 'D', res_cost=[1, 0.1], weight=0)
        self.H.add_edge('D', 'Sink', res_cost=[1, 0.1], weight=0)

        # Create digraph with a resource infeasible minimum cost path
        self.J = DiGraph(directed=True, n_res=2)
        self.J.add_edge('Source', 'A', res_cost=[1, 1], weight=1)
        self.J.add_edge('Source', 'B', res_cost=[1, 1], weight=1)
        self.J.add_edge('Source', 'C', res_cost=[10, 1], weight=10)
        self.J.add_edge('A', 'C', res_cost=[1, 1], weight=1)
        self.J.add_edge('A', 'E', res_cost=[10, 1], weight=10)
        self.J.add_edge('A', 'F', res_cost=[10, 1], weight=10)
        self.J.add_edge('B', 'C', res_cost=[2, 1], weight=-1)
        self.J.add_edge('B', 'F', res_cost=[10, 1], weight=10)
        self.J.add_edge('B', 'E', res_cost=[10, 1], weight=10)
        self.J.add_edge('C', 'D', res_cost=[1, 1], weight=-1)
        self.J.add_edge('D', 'E', res_cost=[1, 1], weight=1)
        self.J.add_edge('D', 'F', res_cost=[1, 1], weight=1)
        self.J.add_edge('D', 'Sink', res_cost=[10, 10], weight=10)
        self.J.add_edge('F', 'Sink', res_cost=[10, 1], weight=1)
        self.J.add_edge('E', 'Sink', res_cost=[1, 1], weight=1)

    def testBothDirections(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(self.G, self.max_res, self.min_res)
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm(
                U=self.max_res[0], L=self.min_res[0])
        self.assertRegex(cm.output[0], 'dynamic')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testForward(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(
            self.G, [200, 20], self.min_res, direction='forward')
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm()
        self.assertRegex(cm.output[0], 'forward')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testBackward(self):
        # Find shortest path of simple test digraph
        alg_obj = BiDirectional(self.G, self.max_res,
                                [-1, 0], direction='backward')
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            alg_obj.name_algorithm()
        self.assertRegex(cm.output[0], 'backward')
        path = alg_obj.run()
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])

    def testDominance(self):
        # Check forward and backward dominance
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
                          'x', [1, 'foo'], 'up')

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

    def testGreedyElim(self):
        self.assertRaises(Exception, GreedyElim.run, self.J, [5, 5], [0, 0])

    def testGRASP(self):
        path = GRASP(self.J, [5, 5], [0, 0], 50, 10).run()
        self.assertEqual(path, ['Source', 'A', 'C', 'D', 'E', 'Sink'])


if __name__ == '__main__':
    unittest.main()
