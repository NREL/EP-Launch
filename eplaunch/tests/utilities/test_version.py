import unittest
import os

from eplaunch.utilities.version import Version


class TestVersion(unittest.TestCase):

    def test_numeric_version_from_string(self):
        v = Version()
        self.assertEqual(v.numeric_version_from_string("8.1.0"), 80100)
        self.assertEqual(v.numeric_version_from_string("8.8.8"), 80808)
        self.assertEqual(v.numeric_version_from_string("8.7"), 80700)
        self.assertEqual(v.numeric_version_from_string("8.6-dfjsuy"), 80600)
        self.assertEqual(v.numeric_version_from_string("8.4.2-dfjsuy"), 80402)
        self.assertEqual(v.numeric_version_from_string("7.12.13"), 71213)

    def test_line_with_no_comment(self):
        v = Version()
        self.assertEqual(v.line_with_no_comment(" object, ! this is a comment"), "object,")
        self.assertEqual(v.line_with_no_comment("! this is a comment"), "")
        self.assertEqual(v.line_with_no_comment(" object, "), "object,")

    def test_check_energyplus_version(self):
        v = Version()

        # the version object is on one line
        file_path = os.path.join(os.path.dirname(__file__), "Minimal.idf")
        is_version_found, version_string, version_number = v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9")
        self.assertEqual(version_number, 80900)

        # the version object is spreads across two lines
        file_path = os.path.join(os.path.dirname(__file__), "Minimal2.idf")
        is_version_found, version_string, version_number = v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9.1")
        self.assertEqual(version_number, 80901)
