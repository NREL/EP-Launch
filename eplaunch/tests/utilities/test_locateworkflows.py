import unittest
import os

from eplaunch.utilities.locateworkflows import LocateWorkflows


class TestLocateWorkflows(unittest.TestCase):

    def test_find(self):
        loc_wf = LocateWorkflows()
        directories = loc_wf.find()
        print(directories)
        tests_utilties_energyplus_directory, workflow_folder = os.path.split(directories[0])
        self.assertEqual(workflow_folder, "workflows")
        tests_utilities_directory, energyplus_folder = os.path.split(tests_utilties_energyplus_directory)
        self.assertEqual(energyplus_folder, "EnergyPlusV7-9-0")
