import os
import shutil
import unittest

from eplaunch.utilities.crossplatform import Platform
from eplaunch.utilities.locateworkflows import LocateWorkflows


# Lots of pragma: no cover tags in here.  We won't be able to provide test coverage of all the platforms in one build
# environment, so there's no point counting that against us in coverage measurement.  In the same way, there is a lot of
# error handling for weird OS cases where a file can't be created or something else, that we can't easily recreate.


class TestLocateWorkflows(unittest.TestCase):

    def setUp(self):
        if Platform.get_current_platform() == Platform.WINDOWS:  # pragma: no cover
            current_directory = 'c:\\'
        elif Platform.get_current_platform() == Platform.LINUX:
            current_directory = '/tmp/'
        elif Platform.get_current_platform() == Platform.MAC:  # pragma: no cover
            current_directory = '/tmp'
        else:  # pragma: no cover
            self.fail("Could not identify platform, what platform is this being tested on?")
        self.energyplus_directory = os.path.join(current_directory, "EnergyPlusV5-9-0")
        if not os.path.isdir(self.energyplus_directory):
            try:
                os.mkdir(self.energyplus_directory)
            except OSError:  # pragma: no cover
                print("cannot make energyplus directory")
        self.workflow_directory = os.path.join(self.energyplus_directory, "workflows")
        if not os.path.isdir(self.workflow_directory):
            try:
                os.mkdir(self.workflow_directory)
            except OSError:  # pragma: no cover
                print("cannot make workflow directory")

    def test_locate_workflow_directories(self):
        loc_wf = LocateWorkflows()
        directories = loc_wf.find_eplus_workflows()
        directories59 = [dir for dir in directories if "5-9" in dir]
        tests_utilities_energyplus_directory, workflow_folder = os.path.split(directories59[0])
        self.assertEqual(workflow_folder, "workflows")
        tests_utilities_directory, energyplus_folder = os.path.split(tests_utilities_energyplus_directory)
        self.assertEqual(energyplus_folder, "EnergyPlusV5-9-0")

    @unittest.skipUnless(Platform.get_current_platform() == Platform.LINUX,
                         "Only run test_getting_energyplus_versions_from_binary on Linux")
    def test_getting_energyplus_versions_from_binary(self):

        loc_wf = LocateWorkflows()
        workflow_directories = list(loc_wf.find_eplus_workflows())

        # as a part of this test, we are mocking the energyplus binary itself with a simple script that returns version
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mock_energyplus_path = os.path.join(dir_path, 'mock', 'energyplus')
        test_energyplus_folder = os.path.join(os.path.dirname(workflow_directories[0]))
        shutil.copy(mock_energyplus_path, test_energyplus_folder)

        loc_wf.get_energyplus_versions()
        self.assertEqual(1, len(loc_wf.list_of_energyplus_versions))
        self.assertEqual('5.9.0', loc_wf.list_of_energyplus_versions[0]['version'])
        self.assertEqual('deadbeef00', loc_wf.list_of_energyplus_versions[0]['sha'])

    def test_getting_energyplus_versions_from_idd(self):

        loc_wf = LocateWorkflows()
        workflow_directories = list(loc_wf.find_eplus_workflows())
        workflow_directories.sort()

        # as a part of this test, we are mocking the energyplus IDD with a small dummy version
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mock_idd_path = os.path.join(dir_path, 'mock', 'Energy+.idd')
        test_energyplus_folder = os.path.join(os.path.dirname(workflow_directories[0]))
        shutil.copy(mock_idd_path, test_energyplus_folder)

        loc_wf.get_energyplus_versions()
        self.assertEqual('5.9.0', loc_wf.list_of_energyplus_versions[0]['version'])
        self.assertEqual('deadbeef01', loc_wf.list_of_energyplus_versions[0]['sha'])

    def test_get_workflow_directory(self):

        loc_wf = LocateWorkflows()
        loc_wf.list_of_energyplus_versions = [
            {'version': 1.0, 'workflow': 'first'},
            {'version': 2.0, 'workflow': 'second'},
            {'version': 3.0, 'workflow': 'third'}
        ]
        self.assertEqual('first', loc_wf.get_workflow_directory(1.0))
        self.assertEqual('second', loc_wf.get_workflow_directory(2.0))
        self.assertEqual('third', loc_wf.get_workflow_directory(3.0))
        self.assertEqual('', loc_wf.get_workflow_directory(4.0))

    def tearDown(self):
        try:
            shutil.rmtree(self.workflow_directory)
        except OSError:  # pragma: no cover
            print("cannot remove workflow directory")
        try:
            shutil.rmtree(self.energyplus_directory)
        except OSError:  # pragma: no cover
            print("cannot remove energyplus directory")
