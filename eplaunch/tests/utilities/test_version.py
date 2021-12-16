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
        self.assertEqual(self.v.numeric_version_from_string("1.2-a765aae"), 10200)
        self.assertEqual(self.v.numeric_version_from_string("1.2.0"), 10200)
        self.assertEqual(self.v.numeric_version_from_string("2.3.0"), 20300)
        self.assertEqual(self.v.numeric_version_from_string("13.4.0"), 130400)
        self.assertEqual(self.v.numeric_version_from_string("13.4.7"), 130400)
        self.assertEqual(self.v.numeric_version_from_string("13.4.7", False), 130407)

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
        self.assertEqual('', version_number)

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
        dash_string = '13-4-7'
        numeric = self.v.numeric_version_from_dash_string(dash_string, False)
        self.assertEqual(numeric, 130407)

    def test_string_version_from_number(self):
        original_number = 10000
        string_version = self.v.string_version_from_number(original_number)
        self.assertEqual('V010000', string_version)

    def test_get_get_github_list_of_releases(self):
        repo_url = r'https://api.github.com/repos/NREL/energyplus/releases'
        releases, ok = self.v.get_github_list_of_releases(repo_url)
        if ok:
            self.assertTrue(len(releases) > 0)

    def test_latest_release(self):
        releases = ['1.2.1', '1.3.2', '1.4.3']
        latest, _ = self.v.latest_release(releases)
        self.assertEqual(latest, '1.4.3')
        releases = ['2.4.7', '2.2.4', '2.3.3']
        latest, _ = self.v.latest_release(releases)
        self.assertEqual(latest, '2.4.7')
        releases = ['v3.8.1', 'v3.6.2', 'v3.5.3']
        latest, _ = self.v.latest_release(releases)
        self.assertEqual(latest, '3.8.1')
        releases = ['8.9.0', '9.1.0', '9.6.0']
        latest, _ = self.v.latest_release(releases)
        self.assertEqual(latest, '9.6.0')
        releases = ['9.1.0', '22.1.0', '9.6.0']
        latest, _ = self.v.latest_release(releases)
        self.assertEqual(latest, '22.1.0')

    def test_versions_from_contexts(self):
        contexts = ['EnergyPlus-9.4.0-998c4b761e', ]
        versions = self.v.versions_from_contexts(contexts)
        self.assertEqual(versions, ['9.4.0', ])

        contexts = ['EnergyPlus-9.4.0-998c4b761e', 'NotEP-9.5.0-767867676', 'EnergyPlus-9.3.0-1212112']
        versions = self.v.versions_from_contexts(contexts)
        self.assertEqual(versions, ['9.4.0', '9.3.0'])
