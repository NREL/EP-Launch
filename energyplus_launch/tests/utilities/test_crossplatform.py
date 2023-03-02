import unittest

from energyplus_launch.utilities.crossplatform import Platform


class TestCrossPlatform(unittest.TestCase):

    def test_getting_platforms(self):
        # this is super tough to test, because the test can be run on any platform
        # thus we can't hard-wire an expected response into an assert
        # We could retrieve the platform using a different method, but that seems silly
        # What we are really testing is whether the function can convert a string into a proper enum
        # So I added a test_name argument to the function where we can pass in each string and make sure the
        #  correct enum is passed back for all known platforms
        p = Platform()
        self.assertEqual(Platform.WINDOWS, p.get_current_platform('Windows'))
        self.assertEqual(Platform.LINUX, p.get_current_platform('Linux'))
        self.assertEqual(Platform.MAC, p.get_current_platform('Darwin'))
        self.assertEqual(Platform.UNKNOWN, p.get_current_platform('Commodore'))
