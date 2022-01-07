import unittest

from numpy import testing
from networkx import DiGraph

from cspy import BiDirectional


def createG():
    H = DiGraph(directed=True, n_res=2)
    H.add_nodes_from(['Source', 1, 2, 3, 4, 'Sink'])
    H.add_edge(2, 3, res_cost=[1, 1], weight=1)
    H.add_edge(3, 4, res_cost=[1, 1], weight=1)
    H.add_edge(4, 'Sink', res_cost=[1, 1], weight=1)

    return H


class TestsIssue90(unittest.TestCase):
    """
    Tests for issue #90
    https://github.com/torressa/cspy/issues/90
    """

    def setUp(self):
        self.max_res = [6, 100]
        self.min_res = [0, -100]

        # This works
        self.H = createG()
        self.H.add_edge('Source', 1, res_cost=[1, 1], weight=1)
        self.H.add_edge(1, 2, res_cost=[1, -1], weight=1)

        self.H2 = createG()
        self.H2.add_edge('Source', 1, res_cost=[1, -1], weight=1)
        self.H2.add_edge(1, 2, res_cost=[1, 1], weight=1)

        self.result_path = ['Source', 1, 2, 3, 4, 'Sink']
        self.total_cost = 5.0
        self.consumed_resources = [5.0, 3.0]

    def test_forward(self):
        alg = BiDirectional(self.H,
                            self.max_res,
                            self.min_res,
                            elementary=True,
                            direction="forward")

        alg.run()
        print()
        print(alg.path)
        print()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources,
                                    self.consumed_resources))

    def test_both(self):
        alg = BiDirectional(self.H, self.max_res, self.min_res, elementary=True)
        alg.run()
        print(alg.path)
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources,
                                    self.consumed_resources))

    def test_H2_forward(self):
        alg = BiDirectional(self.H2,
                            self.max_res,
                            self.min_res,
                            elementary=True,
                            direction="forward")
        alg.run()
        print("h2 forward", alg.path)
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources,
                                    self.consumed_resources))

    def test_H2_both(self):
        alg = BiDirectional(self.H2,
                            self.max_res,
                            self.min_res,
                            elementary=True)
        alg.run()
        print("h2 both", alg.path)
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources,
                                    self.consumed_resources))
