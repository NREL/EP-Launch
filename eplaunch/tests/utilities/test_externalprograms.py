import unittest
from eplaunch.utilities.externalprograms import EPLaunchExternalPrograms


class TestCrossPlatform(unittest.TestCase):

    def test_remove_leading_period(self):
        external_runner = EPLaunchExternalPrograms()
        self.assertEqual('txt', external_runner.remove_leading_period('.txt'))
