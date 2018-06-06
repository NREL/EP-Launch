import unittest

from eplaunch.utilities.unittestutilities import UnitTestUtilities


class TestUnitTestUtilities(unittest.TestCase):

    def test_in_unit_test(self):
        utu = UnitTestUtilities()
        self.assertTrue(utu.in_unit_test())
