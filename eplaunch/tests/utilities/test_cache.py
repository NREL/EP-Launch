import json
import os
import tempfile
import unittest

from eplaunch.utilities.cache import CacheFile as cf
from eplaunch.utilities.exceptions import EPLaunchFileException


def create_workflow_file_in_dir(cache_file_path, create_root=True):
    with open(cache_file_path, 'w') as f:
        if create_root:
            f.write(json.dumps({cf.RootKey: {}}, indent=2))
        else:
            pass


class TestCacheFileInitialization(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, cf.FileName)

    def test_empty_directory_creates_cache_file(self):
        cf(working_directory=self.temp_dir).write()
        self.assertTrue(os.path.exists(self.test_cache_file_path))

    def test_reading_existing_valid_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)

    def test_reading_existing_malformed_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path, create_root=False)
        with self.assertRaises(EPLaunchFileException):
            cf(working_directory=self.temp_dir)

    def test_skips_writing_clean_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.write()
        self.assertFalse(c.dirty)


class TestCacheFileAddingResults(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, cf.FileName)

    def test_adding_result_to_empty_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_result('workflowA', 'fileA', {'columnA': 'dataA'})
        self.assertTrue(c.dirty)

    def test_adding_result_to_existing_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {}}
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_files(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {}
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {
                    'fileA': {}
                }
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_results(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {
                    'fileA': {
                        cf.ResultsKey: {
                            'columnB': 'dataB'
                        }
                    }
                }
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertNotIn(
            'columnB', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ResultsKey]
        )
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ResultsKey]['columnA']
        )


class TestCacheFileAddingConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, cf.FileName)

    def test_adding_config_to_empty_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_config('workflowA', 'fileA', {'columnA': 'dataA'})
        self.assertTrue(c.dirty)

    def test_adding_config_to_existing_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {}
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_files(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {}
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {
                    'fileA': {}
                }
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_config(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = cf(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[cf.RootKey] = {
            'existingWorkflow': {
                cf.FilesKey: {
                    'fileA': {
                        cf.ParametersKey: {
                            'columnB': 'dataB'
                        }
                    }
                }
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[cf.RootKey])
        self.assertIn('fileA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey])
        self.assertEqual(
            'dataB', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ParametersKey]['columnB']
        )
        self.assertEqual(
            'dataA', c.workflow_state[cf.RootKey]['existingWorkflow'][cf.FilesKey]['fileA'][cf.ParametersKey]['columnA']
        )