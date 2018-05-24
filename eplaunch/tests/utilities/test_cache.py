import json
import os
import tempfile
import unittest

from eplaunch.utilities.cache import CacheFile
from eplaunch.utilities.exceptions import EPLaunchFileException


class TestCacheFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, CacheFile.FileName)

    def createWorkflowFileInDir(self, create_root=True):
        with open(self.test_cache_file_path, 'a') as f:
            if create_root:
                f.write(json.dumps({CacheFile.RootKey: {}}, indent=2))
            else:
                pass

    def test_empty_directory_creates_cache_file(self):
        CacheFile(working_directory=self.temp_dir).write()
        self.assertTrue(os.path.exists(self.test_cache_file_path))

    def test_reading_existing_valid_cache_file(self):
        self.createWorkflowFileInDir()
        c = CacheFile(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)

    def test_reading_existing_malformed_cache_file(self):
        self.createWorkflowFileInDir(create_root=False)
        with self.assertRaises(EPLaunchFileException):
            CacheFile(working_directory=self.temp_dir)

    def test_adding_result_to_cache_file(self):
        c = CacheFile(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_result('workflowA', 'fileA', {'columnA': 'dataA'})
        self.assertTrue(c.dirty)
        # if workflow_name not in self.workflow_state[self.RootKey]:
        #     self.workflow_state[self.RootKey][workflow_name] = {'files': {}}
        # self.workflow_state[self.RootKey][workflow_name]['files'][file_name] = column_data
