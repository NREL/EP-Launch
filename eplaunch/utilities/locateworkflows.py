import glob
import os
import re
import string
import subprocess

from eplaunch.utilities.crossplatform import Platform


class LocateWorkflows(object):

    def __init__(self):
        self.list_of_found_directories = []
        self.list_of_energyplus_applications = []
        self.list_of_energyplus_versions = []

    def find(self):
        search_roots = {
            Platform.WINDOWS: ["%s:\\" % c for c in string.ascii_uppercase],
            Platform.LINUX: ['/usr/local/bin/', '/tmp/', '/home/edwin/Programs/'],
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
        ep_names = {
            Platform.WINDOWS: 'energyplus.exe',
            Platform.LINUX: 'energyplus',
            Platform.MAC: 'energyplus',
            Platform.UNKNOWN: ''
        }
        for workspace_directory in self.list_of_found_directories:
            energyplus_directory, folder_name = os.path.split(workspace_directory)
            energyplus_application = os.path.join(energyplus_directory, ep_names[Platform.get_current_platform()])
            energyplus_idd = os.path.join(energyplus_directory, 'Energy+.idd')
            if os.path.exists(energyplus_application):
                self.list_of_energyplus_applications.append(energyplus_application)
                found, version_string, build_string = self.get_specific_version_from_exe(energyplus_application)
                if found:
                    self.list_of_energyplus_versions.append({'version': version_string, 'sha': build_string, 'workflow': workspace_directory})
            elif os.path.exists(energyplus_idd):
                found, version_string, build_string = self.get_specific_version_from_idd(energyplus_directory)
                if found:
                    self.list_of_energyplus_versions.append({'version': version_string, 'sha': build_string, 'workflow': workspace_directory})
        return self.list_of_energyplus_versions

    def get_specific_version_from_exe(self, path_to_energyplus_app):
        # print("Getting version from exe: ", path_to_energyplus_app)
        try:
            completed = subprocess.run([path_to_energyplus_app, "--version"], stdout=subprocess.PIPE, timeout=1)
            output_line = completed.stdout
            output_line_string = output_line.decode("utf-8")
            search_regex = r"(?P<version>\d.\d.\d)\W+(?P<sha>[0-9a-f]{10})"
            regex = re.compile(search_regex)
            match = regex.search(output_line_string)
            if match:
                matches = match.groupdict()
                return True, matches['version'], matches['sha']
            else:
                return False, '', ''  # pragma: no cover
        except subprocess.TimeoutExpired:  # pragma: no cover  -- yeah that would be tough to test...
            print("timeout occurred")
            return False, '', ''

    def get_specific_version_from_idd(self, path_to_energyplus_directory):
        # print("Getting version from idd in directory: ", path_to_energyplus_directory)
        idd_loc = os.path.join(path_to_energyplus_directory, "Energy+.idd")
        with open(idd_loc, "r") as file:
            idd_line = file.readline().strip()
            build_line = file.readline().strip()
            two_lines = idd_line + build_line
            search_regex = r"(?P<version>\d.\d.\d)!IDD_BUILD (?P<sha>[0-9a-f]{10})"
            regex = re.compile(search_regex)
            match = regex.search(two_lines)
            if match:
                matches = match.groupdict()
                return True, matches['version'], matches['sha']
            else:
                return False, '', ''  # pragma: no cover

    def get_workflow_directory(self, version_string):
        for version_dictionary in self.list_of_energyplus_versions:
            if version_dictionary['version'] == version_string:
                return version_dictionary['workflow']
        else:
            return ''
