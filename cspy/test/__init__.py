mport unittest

from .tests import TestsBasic


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestsBasic))
    unittest.TextTestRunner(verbosity=2).run(suite)
