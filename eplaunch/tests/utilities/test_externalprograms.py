import unittest
from eplaunch.utilities.externalprograms import EPLaunchExternalPrograms


class TestCrossPlatform(unittest.TestCase):

    def test_remove_leading_period(self):
        external_runner = EPLaunchExternalPrograms()
        self.assertEqual('txt', external_runner.remove_leading_period('.txt'))

    def test_replace_extension_with_suffix(self):
        external_runner = EPLaunchExternalPrograms()
        self.assertEqual('test.csv', external_runner.replace_extension_with_suffix('test.idf', '.csv'))
        self.assertEqual('testout.csv', external_runner.replace_extension_with_suffix('test.idf', 'out.csv'))
