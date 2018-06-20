import os
import glob
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
        ep_names = {
            Platform.WINDOWS: 'energyplus.exe',
            Platform.LINUX: 'energyplus',
            Platform.MAC: 'energyplus',
            Platform.UNKNOWN: ''
        }
        for workspace_directory in self.list_of_found_directories:
            energyplus_directory, folder_name = os.path.split(workspace_directory)
            energyplus_application = os.path.join(energyplus_directory, ep_names[Platform.get_current_platform()])
            if os.path.exists(energyplus_application):
                self.list_of_energyplus_applications.append(energyplus_application)
                found, version_string, build_string = self.get_specific_version_from_exe(energyplus_application)
                if found:
                    self.list_of_energyplus_versions.append({'version': version_string, 'sha': build_string})
                else:
                    found, version_string, build_string = self.get_specific_version_from_idd(energyplus_directory)
        print(self.list_of_energyplus_applications)

    def get_specific_version_from_exe(self, path_to_energyplus_app):
        print("Getting version from exe: ", path_to_energyplus_app)
        output_line_string = ""
        try:
            completed = subprocess.run([path_to_energyplus_app, "--version"], stdout=subprocess.PIPE, timeout=1)
            output_line = completed.stdout
            output_line_string = output_line.decode("utf-8")
        except subprocess.TimeoutExpired:  # pragma: no cover  -- yeah that would be tough to test...
            print("timeout occurred")
        print(output_line_string)
        if ',' in output_line_string:
            _, full_version_string = output_line_string.split(',')
            full_version_string = full_version_string.strip()
            three_number_version, sha_string = full_version_string.split('-')
            _, three_number_version = three_number_version.split(' ')
            print("==================")
            print(three_number_version)
            print(sha_string)
            print("------------------")
            return True, three_number_version, sha_string
        else:
            return False, "", ""

    def get_specific_version_from_idd(self, path_to_energyplus_directory):
        print("Getting version from idd in directory: ", path_to_energyplus_directory)
        idd_loc = os.path.join(path_to_energyplus_directory, "Energy+.idd")
        three_number_version = ""
        sha_string = ""
        if os.path.exists(idd_loc):
            iddline = ""
            buildline = ""
            with open(idd_loc, "r") as file:
                iddline = file.readline()
                buildline = file.readline()
            iddline = iddline.strip()
            buildline = buildline.strip()
            if " " in iddline:
                idd_version_keyword, three_number_version = iddline.split(" ")
                if idd_version_keyword != "!IDD_Version":
                    three_number_version = ""
            if " " in buildline:
                idd_build_keyword, sha_string = buildline.split(" ")
                if idd_build_keyword != "!IDD_BUILD":
                    sha_string = ""
        print("==================")
        print(three_number_version)
        print(sha_string)
        print("------------------")
        if three_number_version != "":
            return True, three_number_version, sha_string
        else:
            return False, three_number_version, sha_string
