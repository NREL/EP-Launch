import json
import os
from eplaunch.interface.exceptions import EPLaunchFileException


class CacheFile(object):
    """
    Represents the file that is kept in each folder where workflows have been started
    Keeps track of the most recent state of the file, with some metadata that is workflow dependent
    """
    FileName = '.eplaunch3'

    def __init__(self, working_directory):
        self.file_path = os.path.join(working_directory, self.FileName)
        if os.path.exists(self.file_path):
            self.workflow_state = self.read()
        else:
            self.workflow_state = {'workflows': []}

    def read(self):
        try:
            body_text = open(self.file_path, 'r').read()
        except IOError:
            raise EPLaunchFileException(self.file_path, 'Could not open or read text from file')
        try:
            cache_object = json.loads(body_text)
        except json.decoder.JSONDecodeError:
            raise EPLaunchFileException(self.file_path, 'Could not parse cache file JSON text')
        print(cache_object['workflows'])

    def write(self):
        body_text = json.dumps(self.workflow_state)
        try:
            open(self.file_path, 'w').write(body_text)
        except IOError:
            raise EPLaunchFileException(self.file_path, 'Could not write cache file')
