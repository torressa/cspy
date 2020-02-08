import sys
import unittest

sys.path.append("../examples/")

from cgar.read_input import read_input
from cgar.algorithm import algorithm


class TestsExamples(unittest.TestCase):
    """
    Tests for the examples directory
    """

    def setUp(self):
        self.airline = 'Finnair'
        self.DataObj = read_input(airline=self.airline)

    def testCGAR(self):
        """
        Tests for the column generation example.
        Dummy test to ensure that the example runs correctly.
        """
        self.assertEqual(
            algorithm(self.DataObj, n_runs=50, airline=self.airline), None)


if __name__ == '__main__':
    unittest.main()
