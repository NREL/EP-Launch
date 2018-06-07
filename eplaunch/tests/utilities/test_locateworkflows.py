import unittest
import os

from eplaunch.utilities.locateworkflows import LocateWorkflows
from eplaunch.utilities.crossplatform import Platform


class TestLocateWorkflows(unittest.TestCase):

    def setUp(self):
        if Platform.get_current_platform() == Platform.WINDOWS:
            current_directory = 'c:\\'
        elif Platform.get_current_platform() == Platform.LINUX:
            current_directory = '/usr/local/bin/'
        elif Platform.get_current_platform() == Platform.MAC:
            current_directory = '/Applications/'
        else:
            current_directory = '/usr/local/bin/'
        self.energyplus_directory = os.path.join(current_directory, "EnergyPlusV5-9-0")
        if not os.path.isdir(self.energyplus_directory):
            try:
                os.mkdir(self.energyplus_directory)
            except:
                print("cannot make energyplus directory")
        self.workflow_directory = os.path.join(self.energyplus_directory, "workflows")
        if not os.path.isdir(self.workflow_directory):
            try:
                os.mkdir(self.workflow_directory)
            except:
                print("cannot make workflow directory")

    def test_find(self):
        if Platform.get_current_platform() == Platform.WINDOWS:
            loc_wf = LocateWorkflows()
            directories = loc_wf.find()
            directories59 = [dir for dir in directories if "5-9" in dir]
            tests_utilties_energyplus_directory, workflow_folder = os.path.split(directories59[0])
            self.assertEqual(workflow_folder, "workflows")
            tests_utilities_directory, energyplus_folder = os.path.split(tests_utilties_energyplus_directory)
            self.assertEqual(energyplus_folder, "EnergyPlusV5-9-0")

    def tearDown(self):
        try:
            os.rmdir(self.workflow_directory)
        except:
            print("cannot remove workflow directory")
        try:
            os.rmdir(self.energyplus_directory)
        except:
            print("cannot remove energyplus directory")
