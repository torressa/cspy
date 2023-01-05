import unittest

from numpy import testing


class TestingBase(unittest.TestCase):
    def check_result(self, alg, path, cost, resources, almost=False) -> bool:
        self.assertEqual(alg.path, path)
        if almost:
            self.assertAlmostEqual(alg.total_cost, cost, places=2)
        else:
            self.assertEqual(alg.total_cost, cost)
        self.assertIsNone(testing.assert_allclose(alg.consumed_resources, resources))
