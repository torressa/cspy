import sys
import unittest

from numpy import array
from random import randint
from networkx import DiGraph, astar_path
from parameterized import parameterized

sys.path.append("../")
from cspy.algorithms.tabu import Tabu
from cspy.algorithms.label import Label
from cspy.algorithms.bidirectional import BiDirectional


class TestsIssue25(unittest.TestCase):
    """
    Tests for issue #25
    https://github.com/torressa/cspy/issues/25
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=array([1, 2]), weight=-1)
        self.G.add_edge('A', 'B', res_cost=array([1, 0.3]), weight=-1)
        self.G.add_edge('B', 'C', res_cost=array([1, 3]), weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=array([1, 2]), weight=10)
        self.G.add_edge('C', 'Sink', res_cost=array([1, 10]), weight=-1)

    @parameterized.expand(zip(range(100), range(100)))
    def testBiDirectionalBothDynamic(self, _, seed):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm for a range of seeds.
        Note the first argument is required to work using parameterized and unittest.
        """
        bidirec = BiDirectional(self.G, self.max_res, self.min_res, seed=seed)
        # Check classification
        with self.assertLogs('cspy.algorithms.bidirectional') as cm:
            bidirec.name_algorithm()
        # Log should contain the word 'dynamic'
        self.assertRegex(cm.output[0], 'dynamic')
        # Check exception for not running first
        with self.assertRaises(Exception) as context:
            bidirec.path
        self.assertTrue("run()" in str(context.exception))
        # Run and test results
        bidirec.run()
        path = bidirec.path
        cost = bidirec.total_cost
        total_res = bidirec.consumed_resources
        self.assertEqual(path, ['Source', 'A', 'B', 'C', 'Sink'])
        self.assertEqual(cost, -13)
        self.assertTrue(all(total_res == [4, 15.3]))


if __name__ == '__main__':
    unittest.main(TestsIssue25())
