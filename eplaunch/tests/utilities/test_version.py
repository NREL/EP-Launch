import os
import unittest

from eplaunch.utilities.crossplatform import Platform
from eplaunch.utilities.version import Version


class TestVersion(unittest.TestCase):

    def setUp(self):
        self.v = Version()

    def test_numeric_version_from_string(self):
        self.assertEqual(self.v.numeric_version_from_string("8.1.0"), 80100)
        self.assertEqual(self.v.numeric_version_from_string("8.8.8"), 80800)
        self.assertEqual(self.v.numeric_version_from_string("8.7"), 80700)
        self.assertEqual(self.v.numeric_version_from_string("8.6-dfjsuy"), 80600)
        self.assertEqual(self.v.numeric_version_from_string("8.4.2-dfjsuy"), 80400)
        self.assertEqual(self.v.numeric_version_from_string("7.12.13"), 71200)
        self.assertEqual(self.v.numeric_version_from_string("22.1"), 220100)
        self.assertEqual(self.v.numeric_version_from_string("28.8.3"), 280800)
        self.assertEqual(self.v.numeric_version_from_string("25.25.25"), 252500)

    def test_line_with_no_comment(self):
        self.assertEqual(self.v.line_with_no_comment(" object, ! this is a comment"), "object,")
        self.assertEqual(self.v.line_with_no_comment("! this is a comment"), "")
        self.assertEqual(self.v.line_with_no_comment(" object, "), "object,")

    def test_check_energyplus_version_one_line(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal.idf")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9")
        self.assertEqual(version_number, 80900)

    def test_check_energyplus_version_imf(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal.imf")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9")
        self.assertEqual(version_number, 80900)

    def test_check_energyplus_version_two_lines(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal2.idf")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9.1")
        self.assertEqual(version_number, 80900)

    def test_check_energyplus_version_epJSON(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal.epJSON")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertTrue(is_version_found)
        self.assertEqual(version_string, "8.9")
        self.assertEqual(version_number, 80900)

    def test_check_energyplus_version_bad_extension(self):
        file_path = os.path.join(os.path.dirname(__file__), "hi.txt")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertFalse(is_version_found)
        self.assertEqual('', version_string)
        self.assertEqual(0, version_number)

    def test_check_energyplus_version_epJSON_no_version(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal_No_Version.epJSON")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertFalse(is_version_found)
        self.assertEqual('', version_string)
        self.assertEqual(0, version_number)

    @unittest.skipUnless(Platform.get_current_platform() == Platform.LINUX,
                         "Test badly encoded file on Linux systems, test fails on Windows")
    def test_check_energyplus_version_bad_file(self):
        file_path = os.path.join(os.path.dirname(__file__), "Minimal_820.idf")
        is_version_found, version_string, version_number = self.v.check_energyplus_version(file_path)
        self.assertFalse(is_version_found)
        self.assertEqual('', version_string)
        self.assertEqual(0, version_number)

    def test_numeric_version_from_dash_string(self):
        dash_string = 'V0-2'
        numeric = self.v.numeric_version_from_dash_string(dash_string)
        self.assertEqual(numeric, 200)  # even though it has a zero appended, it comes back an integer
        dash_string = 'V1-2-0'
        numeric = self.v.numeric_version_from_dash_string(dash_string)
        self.assertEqual(numeric, 10200)
        dash_string = '2-3-0'
        numeric = self.v.numeric_version_from_dash_string(dash_string)
        self.assertEqual(numeric, 20300)
        dash_string = '13-4-0'
        numeric = self.v.numeric_version_from_dash_string(dash_string)
        self.assertEqual(numeric, 130400)

    def test_string_version_from_number(self):
        original_number = 10000
        string_version = self.v.string_version_from_number(original_number)
        self.assertEqual('V010000', string_version)
