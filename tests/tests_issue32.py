import sys
import unittest

from numpy import array
from random import randint
from networkx import DiGraph, astar_path

sys.path.append("../")
from cspy.algorithms.tabu import Tabu
from cspy.algorithms.label import Label
from cspy.algorithms.bidirectional import BiDirectional
from parameterized import parameterized


class TestsIssue32(unittest.TestCase):
    """
    Tests for issue #32
    https://github.com/torressa/cspy/issues/32
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [5, 10e5, 1], [0, 0, 0]
        # Create simple digraph with appropriate attributes
        # No resource costs required for custom REFs
        self.G = DiGraph(directed=True, n_res=3)
        self.G.add_edge('Source', 1, res_cost=array([0, 0, 0]), weight=-1)
        self.G.add_edge(1, 2, res_cost=array([0, 0, 0]), weight=-1)
        self.G.add_edge(2, 3, res_cost=array([0, 0, 0]), weight=-10)
        self.G.add_edge(2, 4, res_cost=array([0, 1, 0]), weight=-10)
        self.G.add_edge(3, 4, res_cost=array([0, 1, 0]), weight=-10)
        self.G.add_edge(4, 'Sink', res_cost=array([0, 0, 0]), weight=-1)

    def custom_REF(self, cumulative_res, edge):
        res_new = array(cumulative_res)
        # Unpack edge
        u, v, edge_data = edge[0:3]
        # Monotone resource
        res_new[0] += 1
        # Increasing resource
        if v == "Sink":
            res_new[1] = res_new[1]
        else:
            res_new[1] += int(v)**2
        # Resource reset
        res_new[2] += edge_data["res_cost"][1]

        return res_new

    @parameterized.expand(zip(range(100), range(100)))
    def testBiDirectionalBothDynamic(self, _, seed):
        """
        Find shortest path of simple test digraph using the BiDirectional
        algorithm for a range of seeds.
        Note the first argument is required to work using parameterized and unittest.
        """
        bidirec = BiDirectional(self.G,
                                self.max_res,
                                self.min_res,
                                REF=self.custom_REF,
                                seed=seed)
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
        self.assertEqual(path, ['Source', 1, 2, 3, 4, 'Sink'])
        self.assertEqual(cost, -23)
        self.assertTrue(all(total_res == [5, 30, 1]))


if __name__ == '__main__':
    unittest.main(TestsIssue32())
