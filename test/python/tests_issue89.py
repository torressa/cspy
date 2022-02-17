from networkx import DiGraph

from cspy import BiDirectional

from utils import TestingBase


class TestsIssue89(TestingBase):
    """
    Tests for issue #89
    https://github.com/torressa/cspy/issues/89
    """

    def setUp(self):
        self.max_res = [10, 100]
        self.min_res = [0, 1]
        rc = [1, 0]

        # Example 1
        # Source -> 0 -> Sink is valid, but not returned.
        self.H = DiGraph(directed=True, n_res=2)
        self.H.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7])

        self.H.add_edge(0, 3, res_cost=rc, weight=1)
        self.H.add_edge(0, 5, res_cost=rc, weight=1)
        self.H.add_edge(0, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge(1, 3, res_cost=rc, weight=1)
        self.H.add_edge(1, 5, res_cost=rc, weight=1)
        self.H.add_edge(1, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge(2, 1, res_cost=rc, weight=1)
        self.H.add_edge(2, 4, res_cost=rc, weight=1)
        self.H.add_edge(2, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge(3, 1, res_cost=rc, weight=1)
        self.H.add_edge(3, 4, res_cost=rc, weight=1)
        self.H.add_edge(3, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge(4, 0, res_cost=rc, weight=1)
        self.H.add_edge(4, 2, res_cost=rc, weight=1)
        self.H.add_edge(4, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge(5, 0, res_cost=rc, weight=1)
        self.H.add_edge(5, 2, res_cost=rc, weight=1)
        self.H.add_edge(5, 'Sink', res_cost=rc, weight=1)
        self.H.add_edge('Source', 0, res_cost=[1, 1], weight=1)
        self.H.add_edge('Source', 1, res_cost=rc, weight=1)
        self.H.add_edge('Source', 2, res_cost=rc, weight=1)
        self.H.add_edge('Source', 3, res_cost=rc, weight=1)
        self.H.add_edge('Source', 4, res_cost=rc, weight=1)
        self.H.add_edge('Source', 5, res_cost=rc, weight=1)

        # Example 2 (subgraph of example 1)
        self.H2 = DiGraph(directed=True, n_res=2)
        self.H2.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7])

        self.H2.add_edge(0, 'Sink', res_cost=rc, weight=1)
        self.H2.add_edge(1, 'Sink', res_cost=rc, weight=1)
        self.H2.add_edge('Source', 0, res_cost=[1, 1], weight=1)
        self.H2.add_edge('Source', 1, res_cost=rc, weight=1)
        self.result_path = ['Source', 0, 'Sink']
        self.total_cost = 2.0
        self.consumed_resources = [2.0, 1.0]

    def test_forward_elementary(self):
        alg = BiDirectional(self.H,
                            self.max_res,
                            self.min_res,
                            elementary=True,
                            direction="forward")
        alg.run()
        self.check_result(alg, self.result_path, self.total_cost,
                          self.consumed_resources)

    def test_both_elementary(self):
        alg = BiDirectional(self.H, self.max_res, self.min_res, elementary=True)
        alg.run()
        self.check_result(alg, self.result_path, self.total_cost,
                          self.consumed_resources)

    def test_H2_forward_elementary(self):
        alg = BiDirectional(self.H2,
                            self.max_res,
                            self.min_res,
                            elementary=True,
                            direction="forward")
        alg.run()
        self.check_result(alg, self.result_path, self.total_cost,
                          self.consumed_resources)

    def test_H2_both_elementary(self):
        alg = BiDirectional(self.H2,
                            self.max_res,
                            self.min_res,
                            elementary=True)
        alg.run()
        self.check_result(alg, self.result_path, self.total_cost,
                          self.consumed_resources)
