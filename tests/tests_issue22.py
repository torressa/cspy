import unittest

from numpy import array
from random import randint
from networkx import DiGraph, astar_path
from parameterized import parameterized

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
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [len(self.G.edges()), 2], [0, 0]
        # Expected results
        self.result_path = ['Source', 2, 1, 'Sink']
        self.total_cost = -10
        self.consumed_resources = [3, 2]

    def test_tabu(self):
        """Find shortest path of simple test digraph using Tabu.
        """
        alg = Tabu(self.G, self.max_res, self.min_res)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))
        self.assertTrue(
            all(e in self.G.edges() for e in zip(alg.path, alg.path[1:])))
        # Check networkx's astar_path
        path_star = astar_path(self.G, "Source", "Sink")
        self.assertEqual(path_star, ['Source', 1, 'Sink'])

    @parameterized.expand(zip(range(100), range(100)))
    def test_bidirectional_random(self, _, seed):
        """
        Test BiDirectional with randomly chosen sequence of directions
        for a range of seeds.
        """
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            seed=seed,
                            elementary=False)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def test_bidirectional_forward(self):
        """
        Find shortest path using BiDirectional algorithm with only forward
        direction.
        """
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='forward',
                            elementary=True)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def test_bidirectional_backward(self):
        """
        Find shortest path of simple test digraph using BiDirectional
        algorithm with only backward direction.
        """
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='backward',
                            elementary=True)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(all(alg.consumed_resources == self.consumed_resources))

    def test_dominance(self):
        # Check forward and backward label dominance
        L1 = Label(-10, "Sink", array([3, 0]), [])
        L2 = Label(0, "Sink", array([1, 0]), [])

        self.assertFalse(L1.dominates(L2, "forward"))
        self.assertFalse(L2.dominates(L1, "forward"))
        self.assertTrue(L1.dominates(L2, "backward"))
        self.assertFalse(L2.dominates(L1, "backward"))

        if not (L1.dominates(L2, "forward") or L2.dominates(L1, "forward")):
            self.assertTrue(L1.dominates(L2, "backward"))
