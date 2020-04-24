import sys
import unittest

from numpy import array
from networkx import DiGraph

sys.path.append("../")
from cspy.algorithms.bidirectional import BiDirectional

from logging import basicConfig, DEBUG

basicConfig(level=DEBUG)


class TestsIssue38(unittest.TestCase):
    """
    Tests for issue #38
    https://github.com/torressa/cspy/issues/38
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        # No resource costs required for custom REFs
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
        self.G.add_edge("A", "Sink", res_cost=array([1, 10]), weight=0)

    def testBiDirectionalBothDynamic(self):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm for a range of seeds.
        Note the first argument is required to work using parameterized and unittest.
        """
        bidirec = BiDirectional(self.G, self.max_res, self.min_res)
        # Run and test results
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', "A", 'Sink'])
        self.assertEqual(cost, 0)
        self.assertTrue(all(total_res == [2, 12]))


if __name__ == '__main__':
    unittest.main(TestsIssue38())
