import json
import os

from eplaunch.utilities.exceptions import EPLaunchFileException


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

    def add_result(self, workflow_name, file_name, column_data):
        self.dirty = True
        if workflow_name not in self.workflow_state[self.RootKey]:
            self.workflow_state[self.RootKey][workflow_name] = {'files': {}}
        self.workflow_state[self.RootKey][workflow_name]['files'][file_name] = column_data

    def read(self):
        try:
            body_text = open(self.file_path, 'r').read()
        except IOError:
            raise EPLaunchFileException(self.file_path, 'Could not open or read text from file')
        try:
            return json.loads(body_text)
        except json.decoder.JSONDecodeError:
            raise EPLaunchFileException(self.file_path, 'Could not parse cache file JSON text')

    def write(self):
        body_text = json.dumps(self.workflow_state, indent=2)
        try:
            open(self.file_path, 'w').write(body_text)
        except IOError:
            raise EPLaunchFileException(self.file_path, 'Could not write cache file')
