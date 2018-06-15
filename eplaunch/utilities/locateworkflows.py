import os
import glob
import string
import subprocess

from eplaunch.utilities.crossplatform import Platform


class LocateWorkflows(object):

    list_of_found_directories = []
    list_of_energyplus_applications = []
    list_of_energyplus_versions =[]

    def find(self):
        search_roots = {
            Platform.WINDOWS: ["%s:\\" % c for c in string.ascii_uppercase],
            Platform.LINUX: ['/usr/local/bin/', '/tmp/'],
            Platform.MAC: ['/Applications/', '/tmp/'],
            Platform.UNKNOWN: [],
        }
        current_search_roots = search_roots[Platform.get_current_platform()]
        search_names = ["EnergyPlus*", "energyplus*", "EP*", "ep*", "E+*", "e+*"]
        found_directories = set()
        for search_root in current_search_roots:
            for search_name in search_names:
                full_search_path = os.path.join(search_root, search_name)
                full_search_path_with_workflow = os.path.join(full_search_path, "workflows")
                possible_directories = glob.glob(full_search_path_with_workflow)
                found_directories.update(possible_directories)
        self.list_of_found_directories = list(found_directories)
        return self.list_of_found_directories

    def get_energyplus_versions(self):
        for workspace_directory in self.list_of_found_directories:
            energyplus_directory, folder_name = os.path.split(workspace_directory)
            energyplus_application = os.path.join(energyplus_directory, "energyplus.exe")
            if os.path.exists(energyplus_application):
                self.list_of_energyplus_applications.append(energyplus_application)
                self.get_specific_version(energyplus_application)
        print(self.list_of_energyplus_applications)

    def get_specific_version(self,path_to_energyplus_app):
        completed = subprocess.run([path_to_energyplus_app,"--version"],stdout=subprocess.PIPE)
        output_line = completed.stdout
        output_line_string = output_line.decode("utf-8")
        _, full_version_string = output_line_string.split(',')
        full_version_string = full_version_string.strip()
        three_number_version, sha_string = full_version_string.split('-')
        _, three_number_version = three_number_version.split(' ')
        print("==================")
        print(three_number_version)
        print(sha_string)
        print("------------------")