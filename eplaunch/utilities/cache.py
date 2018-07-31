import json
import os

from eplaunch.utilities.exceptions import EPLaunchFileException

try:
    from json.decoder import JSONDecodeError
except ImportError:  # pragma: no cover
    JSONDecodeError = ValueError


class CacheFile(object):
    """
    Represents the file that is kept in each folder where workflows have been started
    Keeps track of the most recent state of the file, with some metadata that is workflow dependent
    """
    FileName = '.eplaunch3'
    RootKey = 'workflows'
    FilesKey = 'files'
    ParametersKey = 'config'
    ResultsKey = 'result'
    WeatherFileKey = 'weather'

    def __init__(self, working_directory):
        self.file_path = os.path.join(working_directory, self.FileName)
        if os.path.exists(self.file_path):
            self.workflow_state = self.read()
            self.dirty = False
        else:
            self.workflow_state = {self.RootKey: {}}
            self.dirty = True

    def _add_file_attribute(self, workflow_name, file_name, attribute, data, replace):
        """
        This function generically updates some attribute of a file within a given workflow context
        The hierarchy is:
         workflows
          - workflow_name
           - files
            - file_name
             - attribute
              - data
        The replace parameter states whether the content in attribute will be updated, or replaced, with data

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
            if self.FilesKey in this_workflow:
                these_files = this_workflow[self.FilesKey]
                if file_name in these_files:
                    this_file = these_files[file_name]
                    if replace:
                        this_file[attribute] = data
                    else:
                        if attribute in this_file:
                            this_config = this_file[attribute]
                            merged_config_data = {**this_config, **data}  # merge dicts, avail in Python 3.5+
                            this_file[attribute] = merged_config_data
                        else:
                            this_file[attribute] = data
                else:
                    these_files[file_name] = {attribute: data}
            else:
                this_workflow[self.FilesKey] = {file_name: {attribute: data}}
        else:
            root[workflow_name] = {self.FilesKey: {file_name: {attribute: data}}}

    def add_config(self, workflow_name, file_name, config_data):
        self._add_file_attribute(workflow_name, file_name, self.ParametersKey, config_data, False)

    def add_result(self, workflow_name, file_name, column_data):
        self._add_file_attribute(workflow_name, file_name, self.ResultsKey, column_data, True)

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
        if not self.dirty:
            return
        body_text = json.dumps(self.workflow_state, indent=2)
        try:
            with open(self.file_path, 'w') as f:
                f.write(body_text)
                self.dirty = False
        except IOError:  # pragma: no cover  -- would be difficult to mock up this weird case
            raise EPLaunchFileException(self.file_path, 'Could not write cache file')
