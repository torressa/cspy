import sys
import unittest

from networkx import DiGraph
from numpy import array
from numpy.random import RandomState

sys.path.append("../")
from cspy.preprocessing import check_and_preprocess


class TestsPreprocessing(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    """

    def setUp(self):
        # Create digraph with negative resource costs with unreachable node 'B'
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=array([1, 2]), weight=0)
        self.G.add_edge('A', 'C', res_cost=array([-1, 0.3]), weight=0)
        self.G.add_edge('A', 'B', res_cost=array([-1, 3]), weight=0)
        # Unreachable node B
        self.G.add_edge('B', 'D', res_cost=array([-1, 2]), weight=0)
        self.G.add_edge('C', 'D', res_cost=array([1, 0.1]), weight=0)
        self.G.add_edge('D', 'Sink', res_cost=array([1, 0.1]), weight=0)

        # Create digraph with a resource infeasible minimum cost path
        self.H = DiGraph(directed=True, n_res=2)
        self.H.add_edge('Source', 'A', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('A', 'B', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('B', 'Sink', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('Sink', 'Source', res_cost=array([1, 1]), weight=-1)

    def testUnreachable(self):
        """
        Tests if the unreachable node 'B' is removed.
        """
        self.G = check_and_preprocess(
            True,
            self.G,
            [5, 20],
            [0, 0],
        )
        self.assertTrue('B' not in self.G.nodes())

    def testNegativeCostCycle(self):
        """
        Tests if the right type of exception is raise for a network with a
        negative cost cycle.
        See: https://networkx.github.io/documentation/networkx-1.10/reference/
        generated/networkx.algorithms.shortest_paths.weighted.negative_edge_cycle.html
        """
        with self.assertRaises(Exception) as context:
            check_and_preprocess(False, self.H)
        str(context.exception)
        self.assertTrue(
            str(context.exception) in "A negative cost cycle was found.")


if __name__ == '__main__':
    unittest.main()
