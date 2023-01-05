import unittest
from networkx import DiGraph, read_graphml

from cspy import BiDirectional
from utils import TestingBase


def load_graph():
    G = read_graphml("../test/python/graph104.graphml")
    for e in G.edges(data=True):
        e[2]["res_cost"] = [e[2]["res_cost"]]
        e[2]["weight"] = round(e[2]["weight"], 5)
    return G


@unittest.skip("Skipping test104")
class TestsIssue104(TestingBase):
    """
    Tests for issue #104
    https://github.com/torressa/cspy/issues/104
    """

    def setUp(self):
        self.max_res = [50]
        self.min_res = [0]

        # This works
        self.G = load_graph()

        self.result_path = ["Source", "1", "65", "69", "5", "9", "Sink"]
        self.total_cost = -23.22
        self.consumed_resources = [50.0]

    def test_forward_elementary(self):
        alg = BiDirectional(
            self.G,
            self.max_res,
            self.min_res,
            elementary=True,
            direction="forward",
        )

        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources, almost=True
        )

    # TODO: this is very broken
    # def test_both_elementary(self):
    #     alg = BiDirectional(
    #         self.G,
    #         self.max_res,
    #         self.min_res,
    #         # elementary=True,
    #         two_cycle_elimination=True,
    #     )
    #     alg.run()
    #     self.check_result(
    #         alg, self.result_path, self.total_cost, self.consumed_resources
    #     )
    #
