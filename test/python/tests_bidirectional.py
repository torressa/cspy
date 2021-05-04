import unittest
from time import time

from networkx import DiGraph
from numpy import array

from cspy import BiDirectional


class TestsBiDirectional(unittest.TestCase):
    """
    Tests for finding the resource constrained shortest
    path of simple DiGraph using the BiDirectional algorithm.
    Includes algorithm classification, and some exception handling.
    """

    def setUp(self):
        # Maximum and minimum resource arrays
        self.max_res, self.min_res = [4, 20], [0, 0]
        # Create simple digraph with appropriate attributes
        self.G = DiGraph(directed=True, n_res=2)
        self.G.add_edge('Source', 'A', res_cost=[1, 2], weight=-1)
        self.G.add_edge('A', 'B', res_cost=[1, 0.3], weight=-1)
        self.G.add_edge('B', 'C', res_cost=[1, 3], weight=-10)
        self.G.add_edge('B', 'Sink', res_cost=[1, 2], weight=10)
        self.G.add_edge('C', 'Sink', res_cost=[1, 10], weight=-1)

        self.result_path = ['Source', 'A', 'B', 'C', 'Sink']
        self.total_cost = -13
        self.consumed_resources = [4, 15.3]

    # TODO fix method="random" see issues
    # @parameterized.expand(zip(range(100), range(100)))
    # def test_random(self, _, seed):
    #     'Test method = "random" for a range of seeds'
    #     alg = BiDirectional(self.G,
    #                         self.max_res,
    #                         self.min_res,
    #                         method="random",
    #                         seed=seed)
    #     # Run and test results
    #     alg.run()
    #     self.assertEqual(alg.path, self.result_path)
    #     self.assertEqual(alg.total_cost, self.total_cost)
    #     self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_generated(self):
        'Test method = "generated"'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="generated")
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_processed(self):
        'Test method = "processed"'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="processed")
        alg.run()
        path = alg.path
        cost = alg.total_cost
        total_res = alg.consumed_resources
        self.assertEqual(path, self.result_path)
        self.assertEqual(cost, self.total_cost)
        self.assertTrue(total_res == self.consumed_resources)

    def test_unprocessed(self):
        'Test method = "unprocessed"'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="unprocessed")
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_unprocessed_time_limit(self):
        'Test time_limit parameter'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="unprocessed",
                            time_limit=0.001)
        start = time()
        alg.run()
        self.assertTrue(time() - start <= 0.001 + 1e-3)
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_unprocessed_threshold(self):
        'Test threshold parameter'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="unprocessed",
                            threshold=0)
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_unprocessed_time_limit_threshold(self):
        'Test time_limit and threshold parameters'
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            method="unprocessed",
                            time_limit=0.001,
                            threshold=0)
        start = time()
        alg.run()
        self.assertTrue(time() - start <= 0.001 + 1e-3)
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_forward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='forward')
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_backward(self):
        alg = BiDirectional(self.G,
                            self.max_res,
                            self.min_res,
                            direction='backward')
        # Check path
        alg.run()
        self.assertEqual(alg.path, self.result_path)
        self.assertEqual(alg.total_cost, self.total_cost)
        self.assertTrue(alg.consumed_resources == self.consumed_resources)

    def test_input_exceptions(self):
        # Check whether wrong input raises exceptions
        self.assertRaises(Exception, BiDirectional, self.G, 'x', [1, 'foo'],
                          'up')
