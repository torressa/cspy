import unittest

from numpy import array
from networkx import DiGraph

from cspy.algorithms.bidirectional import (BiDirectional, PyREFCallback,
                                           convert_list_to_double_vector)
from parameterized import parameterized


class MyCallback(PyREFCallback):

    def REF_fwd(self, cumul_res, tail, head, edge_res, partial_path,
                cumul_cost):
        res_new = list(cumul_res)
        # Monotone resource
        res_new[0] += 1.0
        # Increasing resource
        if "Sink" in head:
            res_new[1] = res_new[1]
        else:
            res_new[1] += float(int(head)**2)
        # Resource reset
        res_new[2] += edge_res[1]
        return res_new

    def REF_bwd(self, cumul_res, tail, head, edge_res, partial_path,
                cumul_cost):
        res_new = list(cumul_res)
        # Monotone resource
        res_new[0] -= 1
        # Increasing resource
        if "Sink" in head:
            res_new[1] = res_new[1]
        else:
            res_new[1] += float(int(head)**2)
        # Resource reset
        res_new[2] += edge_res[1]
        return res_new


class TestsIssue32(unittest.TestCase):
    """
    Tests for issue #32
    https://github.com/torressa/cspy/issues/32
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.my_callback = MyCallback()
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
        # Expected results
        self.result_path = ['Source', 1, 2, 3, 4, 'Sink']
        self.total_cost = -23
        self.consumed_resources = [5, 30, 1]

    def test_bidirectional(self):
        """Test BiDirectional with custom callback."""
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="unprocessed",
                            REF_callback=self.my_callback)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertEqual(alg.consumed_resources, self.consumed_resources)

    def test_bidirectional_forward(self):
        """Test BiDirectional with custom callback."""
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction="forward",
                            REF_callback=self.my_callback)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertEqual(alg.consumed_resources, self.consumed_resources)
