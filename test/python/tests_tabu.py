import unittest
from time import time

from networkx import DiGraph
from numpy import array

from cspy.algorithms.tabu import Tabu

from utils import TestingBase


class TestsTabu(TestingBase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the Tabu algorithm.
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge("Source", "A", res_cost=array([1, 2]), weight=-1)
        self.G.add_edge("A", "B", res_cost=array([1, 0.3]), weight=-1)
        self.G.add_edge("B", "C", res_cost=array([1, 3]), weight=-10)
        self.G.add_edge("B", "Sink", res_cost=array([1, 2]), weight=10)
        self.G.add_edge("C", "Sink", res_cost=array([1, 10]), weight=-1)

        self.result_path = ["Source", "A", "B", "C", "Sink"]
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    def test_simple(self):
        alg = Tabu(self.G, self.max_res, self.min_res)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_astar(self):
        alg = Tabu(self.G, self.max_res, self.min_res, algorithm="astar")
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_time_limit(self):
        alg = Tabu(self.G, self.max_res, self.min_res, time_limit=0.001)
        start = time()
        alg.run()
        # Fudge for windows workflow
        self.assertTrue(time() - start <= 0.002)
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_threshold(self):
        alg = Tabu(self.G, self.max_res, self.min_res, threshold=100)
        alg.run()
        self.check_result(alg, ["Source", "A", "B", "Sink"], 8, [3, 4.3])

    def test_time_limit_threshold(self):
        alg = Tabu(self.G, self.max_res, self.min_res, time_limit=0.001, threshold=0)
        start = time()
        alg.run()
        self.assertTrue(time() - start <= 0.002)
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_astar_time_limit(self):
        "time limit parameter"
        alg = Tabu(
            self.G, self.max_res, self.min_res, algorithm="astar", time_limit=0.001
        )
        start = time()
        alg.run()
        self.assertTrue(time() - start <= 0.002)
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_astar_threshold(self):
        "test threshold parameter"
        alg = Tabu(self.G, self.max_res, self.min_res, algorithm="astar", threshold=100)
        alg.run()
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_astar_time_limit_threshold(self):
        "time limit and threshold parameters"
        alg = Tabu(
            self.G,
            self.max_res,
            self.min_res,
            algorithm="astar",
            time_limit=0.001,
            threshold=100,
        )
        start = time()
        alg.run()
        self.assertTrue(time() - start <= 0.002)
        self.check_result(
            alg, self.result_path, self.total_cost, self.consumed_resources
        )

    def test_time_limit_raises(self):
        alg = Tabu(self.G, self.max_res, self.min_res, time_limit=0)
        self.assertRaises(Exception, alg.run)

    def testInputExceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, Tabu, self.G, "x", [1, "foo"], "up")
