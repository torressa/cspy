import unittest

from numpy import testing


class TestingBase(unittest.TestCase):

    def check_result(self, alg, path, cost, resources) -> bool:
        self.assertEqual(alg.path, path)
        self.assertEqual(alg.total_cost, cost)
        self.assertIsNone(
            testing.assert_allclose(alg.consumed_resources, resources))
