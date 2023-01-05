import unittest

from networkx import MultiGraph, DiGraph
from numpy import array

from cspy.checking import check
from cspy.preprocessing import preprocess_graph


class TestsPreprocessing(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    """

    def setUp(self):
        # Create digraph with negative resource costs with unreachable node 'E'
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
        self.G.add_edge("A", "C", res_cost=array([-1, 0.3]), weight=0)
        self.G.add_edge("A", "B", res_cost=array([-1, 3]), weight=0)
        self.G.add_edge("B", "D", res_cost=array([-1, 2]), weight=0)
        # Unreachable node E
        self.G.add_edge("B", "E", res_cost=array([10, 1]), weight=0)
        self.G.add_edge("C", "D", res_cost=array([1, 0.1]), weight=0)
        self.G.add_edge("D", "Sink", res_cost=array([1, 0.1]), weight=0)

        # Create digraph with a resource infeasible minimum cost path
        self.H = MultiGraph(directed=True)
        self.H.add_edge("Source", "A", res_cost=array([1, 1]), weight=-1)
        self.H.add_edge("A", "B", res_cost=array([1, 1]), weight=-1)
        self.H.add_edge("B", "Sink", res_cost=array([1, 1]), weight=-1)
        self.H.add_edge("Sink", "Source", weight=-1)
        self.max_res, self.min_res = ["foo"], ["bar"]

        # Create digraph to test issue 72
        self.F = DiGraph(n_res=1)
        self.F.add_edge("Source", "A", res_cost=array([1]), weight=1)
        self.F.add_edge("A", "B", res_cost=array([10]), weight=1)
        self.F.add_edge("A", "Sink", res_cost=array([1]), weight=1)

    def testUnreachable(self):
        """
        Tests if the unreachable node 'E' is removed.
        """
        self.G = preprocess_graph(self.G, [5, 20], [0, 0], True)
        self.assertTrue("E" not in self.G.nodes())

    def testFindBadNode(self):
        """
        Tests if expensive node 'B' is removed
        """
        self.F = preprocess_graph(self.F, [5], [1], True)
        self.assertTrue("B" not in self.F.nodes())

    def testFormatting(self):
        """
        Check if wrong formatting ang graph attributes raise appropriate error
        messages.
        """
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, self.min_res, 1, "foo", "alg")

        self.assertTrue("REF" in str(context.exception))
        self.assertTrue("Input must be a nx.Digraph()" in str(context.exception))

        # Turn MultiGraph into DiGraph
        self.H = DiGraph(self.H)
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, [1, 2])
        self.assertTrue(
            "Input graph must have 'n_res' attribute" in str(context.exception)
        )
        self.assertTrue(
            "Input graph must have edges with 'res_cost' attribute"
            in str(context.exception)
        )
        self.assertTrue("Input lists have to be equal length" in str(context.exception))
        with self.assertRaises(Exception) as context:
            check(self.H, self.max_res, [2], 1)
        self.assertTrue(
            "Elements of input lists must be numbers" in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
