import sys
import unittest

from networkx import MultiGraph, DiGraph
from numpy import array

sys.path.append("../")

from cspy.checking import check
from cspy.preprocessing import preprocess_graph


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
        self.H = MultiGraph(directed=True)
        self.H.add_edge('Source', 'A', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('A', 'B', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('B', 'Sink', res_cost=array([1, 1]), weight=-1)
        self.H.add_edge('Sink', 'Source', weight=-1)
        self.max_res, self.min_res = ["foo"], ["bar"]

    def testUnreachable(self):
        """
        Tests if the unreachable node 'B' is removed.
        """
        self.G = preprocess_graph(self.G, [5, 20], [0, 0], True)
        self.assertTrue('B' not in self.G.nodes())

    def testNegativeCostCycle(self):
        """
        Tests if the right type of exception is raise for a network with a
        negative cost cycle.
        See: https://networkx.github.io/documentation/networkx-1.10/reference/
        generated/networkx.algorithms.shortest_paths.weighted.negative_edge_cycle.html
        """
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, self.min_res, 1, "foo", "tabu")

        self.assertTrue(
            "A negative cost cycle was found" in str(context.exception))
        self.assertTrue(
            "REF functions must be callable" in str(context.exception))
        self.assertTrue(
            "Input must be a nx.Digraph()" in str(context.exception))
        self.assertTrue(
            "Input direction has to be 'forward', 'backward', or 'both'" in str(
                context.exception))
        self.assertTrue(
            "Resources must be of length >= 2" in str(context.exception))
        # Turn MultiGraph into DiGraph
        self.H = DiGraph(self.H)
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, [1, 2])
        self.assertTrue(
            "Input graph must have 'n_res' attribute" in str(context.exception))
        self.assertTrue("Input graph must have edges with 'res_cost' attribute"
                        in str(context.exception))
        self.assertTrue(
            "Input lists have to be equal length" in str(context.exception))
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, [2], 1)
        self.assertTrue(
            "Elements of input lists must be numbers" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
