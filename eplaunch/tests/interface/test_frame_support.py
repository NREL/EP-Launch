import datetime
import os
import tempfile
import unittest

from eplaunch.interface.frame_support import FrameSupport


class TestGetFilesInDirectory(unittest.TestCase):

    def setUp(self):
        self.new_base_directory = tempfile.mkdtemp()

    def test_empty_directory(self):
        files_in_empty_directory = FrameSupport.get_files_in_directory(self.new_base_directory)
        self.assertIsInstance(files_in_empty_directory, list)
        self.assertEqual(0, len(files_in_empty_directory))

    def test_directory_no_subdirectories(self):
        file_names = ['a', 'b', 'c']
        for filename in file_names:
            full_path = os.path.join(self.new_base_directory, filename)
            open(full_path, 'a').close()
        files_in_directory = FrameSupport.get_files_in_directory(self.new_base_directory)
        self.assertIsInstance(files_in_directory, list)
        self.assertEqual(3, len(files_in_directory))
        for file_structure in files_in_directory:
            # total should be 3 items
            self.assertEqual(3, len(file_structure))
            # name
            self.assertIn('name', file_structure)
            name = file_structure['name']
            self.assertIsInstance(name, str)
            self.assertIn(name, file_names)
            # size
            self.assertIn('size', file_structure)
            size = file_structure['size']
            self.assertIsInstance(size, str)
            # modified
            self.assertIn('modified', file_structure)
            modified = file_structure['modified']
            self.assertIsInstance(modified, datetime.datetime)

    def test_directory_with_dot_files_and_subdirectories(self):
        file_names = ['a', '.b']
        for filename in file_names:
            full_path = os.path.join(self.new_base_directory, filename)
            open(full_path, 'a').close()
        dir_name = 'director'
        full_path = os.path.join(self.new_base_directory, dir_name)
        os.mkdir(full_path)
        files_in_directory = FrameSupport.get_files_in_directory(self.new_base_directory)
        self.assertIsInstance(files_in_directory, list)
        self.assertEqual(1, len(files_in_directory))
