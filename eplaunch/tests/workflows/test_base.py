import unittest

from eplaunch.workflows.base import EPLaunchWorkflowResponse1, BaseEPLaunchWorkflow1


class TestWorkflowResponseConstruction(unittest.TestCase):

    def test_proper_construction(self):
        wfr = EPLaunchWorkflowResponse1(True, 'It is done', {'column1': 'data1'}, extra='data')
        self.assertTrue(wfr.success)
        self.assertEqual(wfr.message, 'It is done')
        self.assertIn('column1', wfr.column_data)
        self.assertIn('extra', wfr.extra_data)


class TestBaseWorkflowMethods(unittest.TestCase):

    def setUp(self):
        self.base_workflow = BaseEPLaunchWorkflow1()

    def test_name_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.name()

    def test_description_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.description()

    def test_get_file_types_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.get_file_types()

    def test_get_output_suffixes_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.get_output_suffixes()

    def test_get_extra_data_optional(self):
        self.base_workflow.get_extra_data()

    def test_get_interface_columns_optional(self):
        self.base_workflow.get_interface_columns()

    def test_main_abstract(self):
        with self.assertRaises(NotImplementedError):
            self.base_workflow.main('run_dir', 'file_name', ['arg1'])
