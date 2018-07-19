import os
from eplaunch.utilities.version import Version

class TransitionVersion(object):

    def __init__(self,worflow_location):

        self.versionclass = Version()
        self.transition_executable_files = self.find_transition_executable_files(worflow_location)
        print(self.transition_executable_files)

    def find_transition_executable_files(self, worflow_location):
        energyplus_root_folder, _ = os.path.split(worflow_location)
        preprocess_folder = os.path.join(energyplus_root_folder, 'PreProcess')
        idfversionupdateer_folder = os.path.join(preprocess_folder, 'IDFVersionUpdater')
        transition_exes = [os.path.abspath(f) for f in os.listdir(idfversionupdateer_folder) if 'Transition-V' in f]
        transition_exes.sort()
        transition_dict = {}
        for transition_exe in transition_exes:
            start_number, end_number = self.get_start_end_version_from_exe(transition_exe)
            transition_dict[start_number] = [end_number, transition_exe]
        return transition_dict

    def get_start_end_version_from_exe(self,exe_file_name):
        if '\\' in exe_file_name:
            parts = exe_file_name.split('\\')
            filename = parts[-1]
        else:
            filename = exe_file_name
        # Transition-V8-8-0-to-V8-9-0.exe
        # 01234567890123456789012345678901234567890
        if filename[:11] == 'Transition-':
            versions_string_with_ext = filename[11:]
            versions_string, _ = versions_string_with_ext.split('.')
            start_version, end_version = versions_string.split('-to-')
            start_number = self.versionclass.numeric_version_from_dash_string(start_version)
            end_number = self.versionclass.numeric_version_from_dash_string(end_version)
            return start_number, end_number
        else:
            return 0,0

    def perform_transition(self,path_to_old_file):
        v = Version()
        is_version_found, original_version_string, original_version_number = v.check_energyplus_version(path_to_old_file)
        print(is_version_found, original_version_string, original_version_number)
        if original_version_number in self.transition_executable_files:
            current_version_number = original_version_number
            while current_version_number in self.transition_executable_files:
                current_version_string = v.string_version_from_number(current_version_number)
                next_version_number, specific_transition_exe = self.transition_executable_files[current_version_number]
                self.run_single_transition(specific_transition_exe, path_to_old_file, current_version_string)
                current_version_number = next_version_number
            final_version_string = v.string_version_from_number(current_version_number)
            return True, 'Version update successful for IDF file {} originally version {} and now version {}'.format(path_to_old_file, original_version_string, final_version_string)
        else:
            return False, 'Updating the IDF file {} that is from version {} is not supported.'.format(path_to_old_file, original_version_string)

    def run_single_transition(self, transition_exe_path, file_to_update, old_verson_string):
        pass
