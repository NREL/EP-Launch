import json
import os
import tempfile
import unittest

from eplaunch.utilities.cache import CacheFile as CF
from eplaunch.utilities.exceptions import EPLaunchFileException


def create_workflow_file_in_dir(cache_file_path, create_root=True):
    with open(cache_file_path, 'w') as f:
        if create_root:
            f.write(json.dumps({CF.RootKey: {}}, indent=2))
        else:
            pass


class TestCacheFileInitialization(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, CF.FileName)

    def test_empty_directory_creates_cache_file(self):
        CF(working_directory=self.temp_dir).write()
        self.assertTrue(os.path.exists(self.test_cache_file_path))

    def test_reading_existing_valid_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)

    def test_reading_existing_malformed_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path, create_root=False)
        with self.assertRaises(EPLaunchFileException):
            CF(working_directory=self.temp_dir)

    def test_skips_writing_clean_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.write()
        self.assertFalse(c.dirty)


class TestCacheFileAddingResults(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, CF.FileName)

    def test_adding_result_to_empty_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_result('workflowA', 'fileA', {'columnA': 'dataA'})
        self.assertTrue(c.dirty)

    def test_adding_result_to_existing_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {}}
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_files(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {}
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {
                    'fileA': {}
                }
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ResultsKey]['columnA']
        )

    def test_adding_result_to_existing_results(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {
                    'fileA': {
                        CF.ResultsKey: {
                            'columnB': 'dataB'
                        }
                    }
                }
            }
        }
        c.add_result('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertNotIn(
            'columnB', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ResultsKey]
        )
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ResultsKey]['columnA']
        )


class TestCacheFileAddingConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, CF.FileName)

    def test_adding_config_to_empty_cache_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_config('workflowA', 'fileA', {'columnA': 'dataA'})
        self.assertTrue(c.dirty)

    def test_adding_config_to_existing_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {}
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_files(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {}
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_file(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {
                    'fileA': {}
                }
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ParametersKey]['columnA']
        )

    def test_adding_config_to_existing_config(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.workflow_state[CF.RootKey] = {
            'existingWorkflow': {
                CF.FilesKey: {
                    'fileA': {
                        CF.ParametersKey: {
                            'columnB': 'dataB'
                        }
                    }
                }
            }
        }
        c.add_config('existingWorkflow', 'fileA', {'columnA': 'dataA'})
        self.assertIn('existingWorkflow', c.workflow_state[CF.RootKey])
        self.assertIn('fileA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey])
        self.assertEqual(
            'dataB', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ParametersKey]['columnB']
        )
        self.assertEqual(
            'dataA', c.workflow_state[CF.RootKey]['existingWorkflow'][CF.FilesKey]['fileA'][CF.ParametersKey]['columnA']
        )


class TestCacheFileUtilityFunctions(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_cache_file_path = os.path.join(self.temp_dir, CF.FileName)

    def test_get_files_for_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        c.add_result('workflowA', 'fileA', {'columnA': 'dataA'})
        c.add_result('workflowA', 'fileB', {'columnA': 'dataB'})
        c.add_result('workflowF', 'fileA', {'columnA': 'dataC'})
        c.add_result('workflowF', 'fileQ', {'columnA': 'dataD'})
        self.assertTrue(c.dirty)
        files_in_workflow = c.get_files_for_workflow('workflowA')
        self.assertIsInstance(files_in_workflow, dict)
        self.assertEqual(2, len(files_in_workflow))
        self.assertListEqual(['fileA', 'fileB'], list(files_in_workflow.keys()))

    def test_get_files_for_empty_workflow(self):
        create_workflow_file_in_dir(self.test_cache_file_path)
        c = CF(working_directory=self.temp_dir)
        self.assertFalse(c.dirty)
        files_in_workflow = c.get_files_for_workflow('workflowA')
        self.assertIsInstance(files_in_workflow, dict)
        self.assertEqual(0, len(files_in_workflow))
