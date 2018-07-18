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
            transition_dict[(start_number, end_number)] = transition_exe
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





