import json
import os

from eplaunch.utilities.exceptions import EPLaunchFileException

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class CacheFile(object):
    """
    Represents the file that is kept in each folder where workflows have been started
    Keeps track of the most recent state of the file, with some metadata that is workflow dependent
    """
    FileName = '.eplaunch3'
    RootKey = 'workflows'

    def __init__(self, working_directory):
        self.file_path = os.path.join(working_directory, self.FileName)
        if os.path.exists(self.file_path):
            self.workflow_state = self.read()
        else:
            self.workflow_state = {self.RootKey: {}}
        self.dirty = False

    def add_config(self, workflow_name, file_name, config_data):
        """
        This function is used to store run configuration data to the cache file
        While the add_result function will completely wipe away the prior results, this function should just update

        :param workflow_name:
        :param file_name:
        :param config_data:
        :return:
        """

        # if there is already a config for this workflow/file, update it
        # if something is missing from the structure, initialize it on each stage
        self.dirty = True
        root = self.workflow_state[self.RootKey]
        if workflow_name in root:
            this_workflow = root[workflow_name]
            if 'files' in this_workflow:
                these_files = this_workflow['files']
                if file_name in these_files:
                    this_file = these_files[file_name]
                    if 'config' in this_file:
                        this_config = this_file['config']
                        merged_config_data = {**this_config, **config_data}  # cool merge for two dicts, avail in 3.5+
                        this_file['config'] = merged_config_data
                    else:
                        this_file['config'] = config_data
                else:
                    these_files[file_name] = {'config': config_data}
            else:
                this_workflow['files'] = {file_name: {'config': config_data}}
        else:
            root[workflow_name] = {'files': {file_name: {'config': config_data}}}

    def add_result(self, workflow_name, file_name, column_data):
        self.dirty = True
        if workflow_name not in self.workflow_state[self.RootKey]:
            self.workflow_state[self.RootKey][workflow_name] = {'files': {}}
        self.workflow_state[self.RootKey][workflow_name]['files'][file_name] = {'result': column_data}

    def read(self):
        try:
            with open(self.file_path, 'r') as f:
                body_text = f.read()
        except IOError:  # pragma: no cover  -- would be difficult to mock up this weird case
            raise EPLaunchFileException(self.file_path, 'Could not open or read text from file')
        try:
            return json.loads(body_text)
        except JSONDecodeError:
            raise EPLaunchFileException(self.file_path, 'Could not parse cache file JSON text')

    def write(self):
        body_text = json.dumps(self.workflow_state, indent=2)
        try:
            with open(self.file_path, 'w') as f:
                f.write(body_text)
        except IOError:  # pragma: no cover  -- would be difficult to mock up this weird case
            raise EPLaunchFileException(self.file_path, 'Could not write cache file')
